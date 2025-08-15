from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from .suggest import suggest

class SuggestView(APIView):
    def post(self, request):
        body = request.data.get("body_markdown")
        if not body:
            return Response({"detail":"body_markdown required"}, status=400)
        tone = request.query_params.get("tone")
        out = suggest(body, tone)
        return JsonResponse(out)