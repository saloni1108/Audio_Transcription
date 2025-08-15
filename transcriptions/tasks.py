from celery import shared_task
from django.conf import settings
from .models import TranscriptionTask, Word, Speaker
from .storage import put_object_and_presign
from .audio_utils import diarize_vad_ecapa
from faster_whisper import WhisperModel
import numpy as np
import librosa
import requests

_model = None

def get_model():
    global _model
    if _model is None:
        _model = WhisperModel("medium", device="cpu", compute_type="int8")
    return _model

@shared_task
def transcribe_task(task_id: str, audio_url: str, content_type: str):
    task = TranscriptionTask.objects.get(id=task_id)
    try:
        resp = requests.get(audio_url, timeout=60)
        resp.raise_for_status()
        audio_bytes = resp.content
        key, _ = put_object_and_presign(audio_bytes, content_type)
        task.audio_s3_key = key
        wav, sr = librosa.load(librosa.util.buf_to_float(audio_bytes), sr=None, mono=True)  # type: ignore
        # librosa can't load raw bytes directly; save temp
        import io, soundfile as sf
        data_io = io.BytesIO(audio_bytes)
        wav, sr = sf.read(data_io, dtype='float32', always_2d=False)

        duration_sec = len(wav) / sr
        task.duration_sec = duration_sec

        # Diarize (lightweight backend)
        diar = diarize_vad_ecapa(np.asarray(wav), int(sr))
        if not diar:
            diar = [(0.0, duration_sec, 0)]

        model = get_model()
        # language auto Detect + word timestamps
        segments, info = model.transcribe(audio=audio_bytes, word_timestamps=True)
        task.language = info.language or "en"
        task.confidence = getattr(info, 'probability', 0.9)

        # Map words to speakers by midpoint
        words = []
        for seg in segments:
            for w in seg.words:
                mid = (w.start + w.end) / 2.0
                spk = 0
                for (s,e,lbl) in diar:
                    if s <= mid <= e:
                        spk = lbl
                        break
                words.append(Word(task=task, word=w.word, start=w.start, end=w.end, speaker_label=f"speaker_{spk+1}"))
        Word.objects.bulk_create(words)

        # Aggregate speakers
        totals = {}
        for (s,e,lbl) in diar:
            totals[f"speaker_{lbl+1}"] = totals.get(f"speaker_{lbl+1}", 0.0) + (e-s)
        Speaker.objects.bulk_create([Speaker(task=task, label=k, total_sec=v) for k,v in totals.items()])

        task.status = "completed"
        task.save()
    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        task.save()
        raise

