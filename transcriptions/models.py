import uuid

from django.db import models


class TranscriptionTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, default="queued")
    language = models.CharField(max_length=8, null=True, blank=True)
    duration_sec = models.FloatField(null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    audio_s3_key = models.CharField(max_length=512, null=True, blank=True)
    error = models.TextField(null=True, blank=True)

class Speaker(models.Model):
    id = models.BigAutoField(primary_key=True)
    task = models.ForeignKey(TranscriptionTask, on_delete=models.CASCADE, related_name="speakers")
    label = models.CharField(max_length=32)
    total_sec = models.FloatField(default=0.0)

class Word(models.Model):
    id = models.BigAutoField(primary_key=True)
    task = models.ForeignKey(TranscriptionTask, on_delete=models.CASCADE, related_name="words")
    word = models.CharField(max_length=128)
    start = models.FloatField()
    end = models.FloatField()
    speaker_label = models.CharField(max_length=32)