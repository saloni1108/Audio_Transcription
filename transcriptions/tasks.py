from celery import shared_task
from django.conf import settings
from .models import TranscriptionTask, Word, Speaker
from .storage import put_object_and_presign
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
        import io, soundfile as sf
        data_io = io.BytesIO(audio_bytes)
        wav, sr = sf.read(data_io, dtype='float32', always_2d=False)

        duration_sec = len(wav) / sr
        task.duration_sec = duration_sec

        model = get_model()

        segments, info = model.transcribe(audio=audio_bytes, word_timestamps=True)
        task.language = info.language or "en"
        task.confidence = getattr(info, 'probability', 0.9)

        words = [
            Word(
                task=task,
                word=w.word,
                start=w.start,
                end=w.end,
                speaker_label="speaker_1"
            )
            for seg in segments
            for w in seg.words
        ]
        Word.objects.bulk_create(words)

        # Create single speaker entry
        Speaker.objects.create(
            task=task,
            label="speaker_1",
            total_sec=duration_sec
        )

        # Mark task as completed
        task.status = "completed"
        task.save()

    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        task.save()
        raise