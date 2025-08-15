from django.urls import path
from .views import TranscribeView, TranscribeStreamView

urlpatterns = [
    path("transcribe", TranscribeView.as_view(), name="transcribe"),
    path("transcribe/<uuid:task_id>/stream", TranscribeStreamView.as_view(), name="transcribe_stream"),
]
