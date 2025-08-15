from django.contrib import admin

from .models import BlogSuggestionLog


@admin.register(BlogSuggestionLog)
class BlogSuggestionLogAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "tone", "meta_description")
    search_fields = ("tone", "meta_description")
    list_filter = ("tone", "created_at")
