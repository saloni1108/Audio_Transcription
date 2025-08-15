from typing import List, Tuple
import numpy as np
import librosa
import soundfile as sf
import webrtcvad
from sklearn.cluster import AgglomerativeClustering

# Lightweight diarization backend using VAD + ECAPA-TDNN embeddings (onnx)
import onnxruntime as ort

class EcapaOnnx:
    _sess = None

    @classmethod
    def _load(cls):
        if cls._sess is None:
            # small public ECAPA ONNX; downloaded at runtime
            import os, pathlib, urllib.request
            path = pathlib.Path("/models/ecapa.onnx")
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                url = "https://huggingface.co/m3hrdadfi/ecapa-tdnn-onnx/resolve/main/model.onnx?download=true"
                urllib.request.urlretrieve(url, path)
            cls._sess = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
        return cls._sess

    @classmethod
    def embed(cls, wav: np.ndarray, sr: int) -> np.ndarray:
        sess = cls._load()
        # downsample to 16000 mono
        if sr != 16000:
            wav = librosa.resample(wav, orig_sr=sr, target_sr=16000)
            sr = 16000
        wav = wav.astype(np.float32)
        inp = wav[np.newaxis, :]
        out = sess.run(None, {sess.get_inputs()[0].name: inp})[0]
        return out[0]


def diarize_vad_ecapa(wav: np.ndarray, sr: int) -> List[Tuple[float,float,int]]:
    """Return list of (start, end, speaker_idx)."""
    vad = webrtcvad.Vad(2)
    frame_ms = 30
    frame_len = int(sr * frame_ms / 1000)

    speech_flags = []
    for i in range(0, len(wav) - frame_len, frame_len):
        frame = (wav[i:i+frame_len] * 32768).astype(np.int16).tobytes()
        speech_flags.append(vad.is_speech(frame, sr))
    speech_flags = np.array(speech_flags)

    # segment speech regions
    segments = []
    start = None
    for idx, flag in enumerate(speech_flags):
        t = idx * frame_ms / 1000.0
        if flag and start is None:
            start = t
        if not flag and start is not None:
            segments.append((start, t))
            start = None
    if start is not None:
        segments.append((start, len(wav)/sr))

    # embed each segment
    embs = []
    for s,e in segments:
        a = int(s*sr)
        b = int(e*sr)
        seg = wav[a:b]
        if len(seg) < sr:  # skip too short
            continue
        embs.append(EcapaOnnx.embed(seg, sr))
    if not embs:
        return []
    embs = np.stack(embs)
    # 2-speaker assumption fallback; can infer via silhouette
    n_speakers = 2 if embs.shape[0] > 1 else 1
    clustering = AgglomerativeClustering(n_clusters=n_speakers, affinity='cosine', linkage='average')
    labels = clustering.fit_predict(embs)

    diar = []
    j = 0
    for (s,e) in segments:
        if int((e-s)*sr) < sr:
            continue
        diar.append((s,e,int(labels[j])))
        j += 1
    return diar
