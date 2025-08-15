import uuid

from django.db import models


class BlogSuggestionLog(models.Model):
    """
    Stores a record of generated blog suggestions for auditing/debugging.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    tone = models.CharField(max_length=50, blank=True, null=True)
    body_markdown = models.TextField()
    suggestions_json = models.JSONField()
    meta_description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"BlogSuggestionLog({self.id})"
