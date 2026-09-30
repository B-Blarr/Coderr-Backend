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
from assistant_app.laya_client import (
    LayaServiceError,
    is_attack,
    score_question,
)
from assistant_app.llm_client import LlmServiceError, answer_question
from assistant_app.quick_replies import quick_reply_kind
from assistant_app.retrieval import keep_relevant, search

from .serializers import QuestionSerializer, SourceSerializer
from .throttling import AssistantGlobalThrottle, AssistantRateThrottle

logger = logging.getLogger(__name__)

SERVICE_ERRORS = (EmbeddingServiceError, LayaServiceError, LlmServiceError)


class AssistantView(APIView):
    """Answers a visitor question from the knowledge base.

    Small talk and obvious nonsense are answered right away. Every other
    question goes through Laya, the search and the similarity threshold
    before Claude writes an answer from the remaining sections. ``kind``
    tells the frontend which case it got.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [AssistantRateThrottle, AssistantGlobalThrottle]

    @extend_schema(exclude=True)
    def post(self, request):
        """Check the question and answer it.

        Excluded from the generated API schema: this endpoint belongs to
        the portfolio and is not part of the Coderr API.
        """
        if not settings.ASSISTANT_ENABLED:
            return self._unavailable()
        serializer = QuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        quick_kind = quick_reply_kind(data['question'])
        if quick_kind:
            return Response({'kind': quick_kind})
        try:
            return self._answer(data['question'], data['lang'])
        except SERVICE_ERRORS as error:
            logger.error("Assistent: %s", error)
            return self._unavailable()

    def check_throttles(self, request):
        """Stop at the first throttle that refuses the request.

        DRF asks every throttle, so an address that is already over its
        own limit would otherwise still use up the global quota.
        """
        for throttle in self.get_throttles():
            if not throttle.allow_request(request, self):
                self.throttled(request, throttle.wait())

    def _answer(self, question, lang):
        """Let Claude answer from the relevant sections, if there are any.

        No section above the threshold and a refusal by Claude both end
        as off_topic, so neither case costs a second request.
        """
        self._reject_attacks(question)
        chunks = keep_relevant(search(question))
        result = (answer_question(question, chunks, lang=lang)
                  if chunks else None)
        if result is None:
            return Response({'kind': 'off_topic'})
        used = [chunks[position - 1] for position in result['sources']]
        return Response({
            'kind': 'answer',
            'answer': result['answer'],
            'answered': result['answered'],
            'sources': SourceSerializer(used, many=True).data,
        })

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

    def _unavailable(self):
        """Answer 503 when the assistant is switched off or broken."""
        return Response(
            {'detail': 'Der Assistent ist gerade nicht verfügbar.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
