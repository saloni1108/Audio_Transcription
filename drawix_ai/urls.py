from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView

from scripts.health_check import check_health
from suggestions.views import SuggestView
from transcriptions.views import TranscribeStreamView, TranscribeView


def healthz(request):
    status = check_health()
    ok = all(v is True for v in status.values())
    return JsonResponse({"ok": ok, "details": status.values()}, status=status)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("/", SpectacularSwaggerView.as_view(url_name="schema")),

    # Auth (JWT)
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),

    # Feature A
    path("api/v1/transcribe", TranscribeView.as_view()),
    path("api/v1/transcribe/<uuid:task_id>/stream", TranscribeStreamView.as_view()),

    # Feature B
    path("api/v1/blog/suggest", SuggestView.as_view()),
]