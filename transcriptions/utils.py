import io
import soundfile as sf

def get_audio_duration(audio_bytes: bytes) -> float:
    """
    Returns the duration of the audio file in seconds.
    """
    data_io = io.BytesIO(audio_bytes)
    wav, sr = sf.read(data_io, dtype='float32', always_2d=False)
    return len(wav) / sr
