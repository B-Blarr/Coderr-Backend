"""Serializers for the assistant app."""

from rest_framework import serializers

from assistant_app.models import KnowledgeChunk


class QuestionSerializer(serializers.Serializer):
    """Validates a visitor question."""

    question = serializers.CharField(max_length=500)


class SourceSerializer(serializers.ModelSerializer):
    """A knowledge section that an answer is based on."""

    class Meta:
        model = KnowledgeChunk
        fields = ('source', 'heading')
