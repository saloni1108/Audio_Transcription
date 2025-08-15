from rest_framework import serializers
from .models import BlogSuggestionLog


class BlogSuggestionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogSuggestionLog
        fields = "__all__"
