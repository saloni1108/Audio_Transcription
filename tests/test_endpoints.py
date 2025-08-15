import pytest
from transcriptions import tasks 

@pytest.mark.parametrize("audio_file", [
    "tests/sample_audio_1.mp4",
])
def test_transcribe_audio(audio_file):
    """Test that transcription returns a non-empty string."""
    result = tasks.transcribe_task(audio_file)
    assert isinstance(result, str)
    assert len(result) > 0

import pytest
from suggestions import suggest  

def test_suggest_keywords():
    """Test that suggestion function returns a list of strings."""
    sample_text = "This is a test transcription"
    result = suggest.suggest(sample_text)
    assert isinstance(result, list)
    assert all(isinstance(item, str) for item in result)
    assert len(result) > 0