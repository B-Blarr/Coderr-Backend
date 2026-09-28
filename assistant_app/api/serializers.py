"""Serializers for the assistant app."""

from rest_framework import serializers

from assistant_app.llm_client import LANGUAGES
from assistant_app.models import KnowledgeChunk


class QuestionSerializer(serializers.Serializer):
    """Validates a visitor question and the language of the page."""

    question = serializers.CharField(max_length=500)
    lang = serializers.ChoiceField(choices=list(LANGUAGES), default='de')


class SourceSerializer(serializers.ModelSerializer):
    """A knowledge section that an answer is based on."""

    class Meta:
        model = KnowledgeChunk
        fields = ('source', 'heading')
