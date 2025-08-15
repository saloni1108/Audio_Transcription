from django.contrib import admin

from .models import Speaker, TranscriptionTask, Word


@admin.register(TranscriptionTask)
class TranscriptionTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "language", "duration_sec", "confidence", "created_at")
    list_filter = ("status", "language")
    search_fields = ("id",)

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "word", "start", "end", "speaker_label")
    list_filter = ("speaker_label",)
    search_fields = ("word",)

@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "label", "total_sec")
    search_fields = ("label",)
