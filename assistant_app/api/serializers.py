"""Serializers for the assistant app."""

from rest_framework import serializers

from assistant_app.models import KnowledgeChunk


class QuestionSerializer(serializers.Serializer):
    """Validates a visitor question."""

    question = serializers.CharField(max_length=500)


class ChunkResultSerializer(serializers.ModelSerializer):
    """One retrieved knowledge section with its similarity score."""

    similarity = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeChunk
        fields = ('source', 'heading', 'content', 'similarity')

    def get_similarity(self, chunk):
        """Turn the cosine distance into a similarity between -1 and 1."""
        return round(1 - chunk.distance, 4)
