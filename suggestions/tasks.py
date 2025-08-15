from celery import shared_task

from .models import BlogSuggestionLog
from .suggest import suggest


@shared_task
def generate_blog_suggestions_task(body_markdown: str, tone: str | None = None) -> dict:
    """
    Celery task to generate blog suggestions and log them in DB.
    """
    suggestions = suggest(body_markdown, tone)

    BlogSuggestionLog.objects.create(
        tone=tone,
        body_markdown=body_markdown,
        suggestions_json=suggestions,
        meta_description=suggestions.get("meta_description", "")
    )

    return suggestions
