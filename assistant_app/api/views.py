"""API views for the assistant app."""

import logging

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from assistant_app.embedding_client import EmbeddingServiceError
from assistant_app.greetings import is_greeting
from assistant_app.laya_client import (
    LayaServiceError,
    is_attack,
    score_question,
)
from assistant_app.retrieval import keep_relevant, search

from .serializers import ChunkResultSerializer, QuestionSerializer
from .throttling import AssistantGlobalThrottle, AssistantRateThrottle

logger = logging.getLogger(__name__)


class AssistantView(APIView):
    """Returns the knowledge sections that best match a question.

    Pure greetings are answered right away, every other question goes
    through Laya first. No language model is involved yet: the response
    shows exactly what retrieval found, so its quality can be measured on
    its own. ``kind`` tells the frontend which case it got.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [AssistantRateThrottle, AssistantGlobalThrottle]

    @extend_schema(exclude=True)
    def post(self, request):
        """Check the question and return the closest sections.

        Excluded from the generated API schema: this endpoint belongs to
        the portfolio and is not part of the Coderr API.
        """
        if not settings.ASSISTANT_ENABLED:
            return self._unavailable()
        serializer = QuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data['question']
        if is_greeting(question):
            return Response({'kind': 'greeting'})
        try:
            self._reject_attacks(question)
            chunks = keep_relevant(search(question))
        except (LayaServiceError, EmbeddingServiceError) as error:
            logger.error("Assistent: %s", error)
            return self._unavailable()
        return self._sections(chunks)

    def check_throttles(self, request):
        """Stop at the first throttle that refuses the request.

        DRF asks every throttle, so an address that is already over its
        own limit would otherwise still use up the global quota.
        """
        for throttle in self.get_throttles():
            if not throttle.allow_request(request, self):
                self.throttled(request, throttle.wait())

    def _reject_attacks(self, question):
        """Raise PermissionDenied when Laya flags the question.

        Only the scores are logged, never the question: visitors' texts
        are not stored anywhere.
        """
        scores = score_question(question)
        if is_attack(scores):
            logger.warning("Assistent: Frage abgelehnt, Werte %s", scores)
            raise PermissionDenied(
                "Diese Frage kann der Assistent nicht beantworten.")

    def _sections(self, chunks):
        """Return the relevant sections, or off_topic when none is left."""
        if not chunks:
            return Response({'kind': 'off_topic', 'results': []})
        results = ChunkResultSerializer(chunks, many=True).data
        return Response({'kind': 'sections', 'results': results})

    def _unavailable(self):
        """Answer 503 when the assistant is switched off or broken."""
        return Response(
            {'detail': 'Der Assistent ist gerade nicht verfügbar.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
