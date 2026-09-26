"""API views for the assistant app."""

import logging

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from assistant_app.embedding_client import EmbeddingServiceError
from assistant_app.retrieval import search

from .serializers import ChunkResultSerializer, QuestionSerializer

logger = logging.getLogger(__name__)


class AssistantView(APIView):
    """Returns the knowledge sections that best match a question.

    No language model is involved yet: the response shows exactly what
    retrieval found, so its quality can be measured on its own.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(exclude=True)
    def post(self, request):
        """Validate the question and return the closest sections.

        Excluded from the generated API schema: this endpoint belongs to
        the portfolio and is not part of the Coderr API.
        """
        if not settings.ASSISTANT_ENABLED:
            return self._unavailable()
        serializer = QuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            chunks = search(serializer.validated_data['question'])
        except EmbeddingServiceError as error:
            logger.error("Assistent: %s", error)
            return self._unavailable()
        results = ChunkResultSerializer(chunks, many=True).data
        return Response({'results': results})

    def _unavailable(self):
        """Answer 503 when the assistant is switched off or broken."""
        return Response(
            {'detail': 'Der Assistent ist gerade nicht verfügbar.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
