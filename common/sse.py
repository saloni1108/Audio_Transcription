import json
from django.http import StreamingHttpResponse


def sse_stream(generator):
    def event_stream():
        for event_name, data in generator:
            yield f"event: {event_name}\n"
            yield f"data: {json.dumps(data)}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    return response
