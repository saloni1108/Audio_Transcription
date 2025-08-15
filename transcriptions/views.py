from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import StreamingHttpResponse
from django.utils.encoding import smart_str
from django.db.models import F
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from .models import TranscriptionTask
from .serializers import TaskSerializer
from django.conf import settings
from .tasks import transcribe_task
from .storage import put_object_and_presign
import mimetypes

class TranscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        url = request.query_params.get("url")
        audio_url = None
        content_type = "audio/mpeg"
        if url:
            audio_url = url
        else:
            file = request.FILES.get("file")
            if not file:
                return Response({"detail":"file or ?url= required"}, status=400)
            if isinstance(file, (InMemoryUploadedFile, TemporaryUploadedFile)):
                data = file.read()
                key, presigned = put_object_and_presign(data, file.content_type or mimetypes.guess_type(file.name)[0] or "application/octet-stream")
                audio_url = presigned
                content_type = file.content_type or "application/octet-stream"
        task = TranscriptionTask.objects.create(status="queued")
        transcribe_task.delay(str(task.id), audio_url, content_type)
        return Response({"task_id": str(task.id)})

class TranscribeStreamView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, task_id):
        def event_stream():
            import time, json
            last_count = 0
            while True:
                task = TranscriptionTask.objects.get(id=task_id)
                d = TaskSerializer(task).data
                yield f"event: status\ndata: {json.dumps({'status': d['status']})}\n\n"
                if d["status"] == "completed":
                    yield f"event: result\ndata: {json.dumps(d)}\n\n"
                    break
                if d["status"] == "failed":
                    yield f"event: error\ndata: {json.dumps({'error': task.error})}\n\n"
                    break
                time.sleep(1)
        resp = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        resp['Cache-Control'] = 'no-cache'
        return resp