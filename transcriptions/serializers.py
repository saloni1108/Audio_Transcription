from rest_framework import serializers
from .models import TranscriptionTask, Word, Speaker

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ("word","start","end","speaker_label")

class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ("label","total_sec")

class TaskSerializer(serializers.ModelSerializer):
    transcript = WordSerializer(source="words", many=True, read_only=True)
    speakers = SpeakerSerializer(source="speakers", many=True, read_only=True)

    class Meta:
        model = TranscriptionTask
        fields = ("id","status","language","duration_sec","confidence","transcript","speakers")
