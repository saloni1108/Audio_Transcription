from django.test import TestCase
from .models import TranscriptionTask, Word, Speaker

class TranscribeModelTests(TestCase):
    def test_create_task(self):
        task = TranscriptionTask.objects.create(status="queued")
        self.assertEqual(task.status, "queued")
        self.assertIsNone(task.language)

    def test_add_word(self):
        task = TranscriptionTask.objects.create(status="completed")
        Word.objects.create(task=task, word="Hello", start=0.0, end=0.5, speaker_label="speaker_1")
        self.assertEqual(task.words.count(), 1)

    def test_add_speaker(self):
        task = TranscriptionTask.objects.create(status="completed")
        Speaker.objects.create(task=task, label="speaker_1", total_sec=3.5)
        self.assertEqual(task.speakers.count(), 1)
