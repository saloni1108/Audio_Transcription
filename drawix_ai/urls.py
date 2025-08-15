from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from transcriptions.views import TranscribeView, TranscribeStreamView
from suggestions.views import SuggestView
from django.http import JsonResponse
from django.conf import settings
import boto3
import redis


def healthz(request):
    # Postgres checked by hitting ORM
    from django.db import connection
    ok = True
    details = {}
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
            details["postgres"] = "ok"
    except Exception as e:
        ok = False
        details["postgres"] = str(e)
    try:
        r = redis.Redis.from_url(settings.REDIS_URL)
        r.ping()
        details["redis"] = "ok"
    except Exception as e:
        ok = False
        details["redis"] = str(e)
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        s3.list_buckets()
        details["s3"] = "ok"
    except Exception as e:
        ok = False
        details["s3"] = str(e)
    status = 200 if ok else 503
    return JsonResponse({"ok": ok, "details": details}, status=status)

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