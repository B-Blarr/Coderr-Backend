"""Tests for the knowledge base, its admin and build_index."""

import json
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework import status

from assistant_app.embedding_client import EmbeddingServiceError
from assistant_app.knowledge_base import KnowledgeBaseError, read_sections
from assistant_app.management.commands.evaluate_retrieval import (
    DEFAULT_QUESTIONS,
)
from assistant_app.models import KnowledgeChunk
from assistant_app.tests.helpers import unit_vector

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / 'knowledge'


class KnowledgeBaseTests(SimpleTestCase):
    """Test how knowledge files are split into sections."""

    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.directory = Path(temp_dir.name)

    def write(self, name, text):
        (self.directory / name).write_bytes(text.encode('utf-8'))

    def test_splits_file_at_headings(self):
        self.write('a.md', "---\nquelle: Q\n---\n\n## One\nFirst.\n"
                           "### Sub\nMore.\n\n## Two\nSecond.\n")
        sections = read_sections(self.directory)
        self.assertEqual(
            [(s.source, s.position, s.heading) for s in sections],
            [('Q', 0, 'One'), ('Q', 1, 'Two')],
        )
        self.assertEqual(sections[0].content, "First.\n### Sub\nMore.")
        self.assertEqual(sections[1].passage, "Two\n\nSecond.")

    def test_reads_bom_and_windows_line_endings(self):
        self.write('a.md', "\ufeff---\r\nquelle: Q\r\n---\r\n## One\r\nA.\r\n")
        section = read_sections(self.directory)[0]
        self.assertEqual((section.heading, section.content), ('One', 'A.'))

    def test_files_are_read_in_name_order(self):
        self.write('b.md', "---\nquelle: B\n---\n## B\nText.\n")
        self.write('a.md', "---\nquelle: A\n---\n## A\nText.\n")
        sources = [s.source for s in read_sections(self.directory)]
        self.assertEqual(sources, ['A', 'B'])

    def test_rejects_malformed_files(self):
        cases = {
            'frontmatter is missing': "## One\nText.\n",
            "'quelle' is missing": "---\ntitel: T\n---\n## One\nText.\n",
            'text before the first': "---\nquelle: Q\n---\nIntro\n## A\nB\n",
            "section 'One' is empty": "---\nquelle: Q\n---\n## One\n## B\nC",
            "no '## ' heading": "---\nquelle: Q\n---\n",
        }
        for message, text in cases.items():
            with self.subTest(message):
                self.write('a.md', text)
                with self.assertRaisesMessage(KnowledgeBaseError, message):
                    read_sections(self.directory)

    def test_rejects_empty_directory(self):
        with self.assertRaisesMessage(KnowledgeBaseError, 'No knowledge'):
            read_sections(self.directory)

    def test_shipped_knowledge_base_is_valid(self):
        sections = read_sections(KNOWLEDGE_DIR)
        self.assertGreater(len(sections), 0)

    def test_shipped_questions_match_shipped_headings(self):
        headings = {s.heading for s in read_sections(KNOWLEDGE_DIR)}
        cases = json.loads(DEFAULT_QUESTIONS.read_text(encoding='utf-8'))
        expected = {h for case in cases for h in case['expected']}
        self.assertEqual(expected - headings, set())


class KnowledgeChunkAdminTests(TestCase):
    """Test the model label and the read-only admin."""

    def test_str_names_source_and_heading(self):
        chunk = KnowledgeChunk(source='Quelle', heading='Titel')
        self.assertEqual(str(chunk), 'Quelle: Titel')

    def test_chunks_cannot_be_added_in_admin(self):
        admin_user = get_user_model().objects.create_superuser(
            username='admin', email='admin@test.de', password='pass1234')
        self.client.force_login(admin_user)
        url = reverse('admin:assistant_app_knowledgechunk_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@patch('assistant_app.management.commands.build_index.embed_passages')
class BuildIndexTests(TestCase):
    """Test the build_index command with the embedding service mocked."""

    def fake_vectors(self, texts):
        return [unit_vector(0) for _ in texts]

    def test_builds_index_from_knowledge_files(self, mock_embed):
        mock_embed.side_effect = self.fake_vectors
        output = StringIO()
        call_command('build_index', stdout=output)
        expected = len(read_sections(KNOWLEDGE_DIR))
        self.assertEqual(KnowledgeChunk.objects.count(), expected)
        self.assertIn(f"Indexed {expected} sections", output.getvalue())

    def test_second_run_replaces_the_index(self, mock_embed):
        mock_embed.side_effect = self.fake_vectors
        call_command('build_index', stdout=StringIO())
        call_command('build_index', stdout=StringIO())
        expected = len(read_sections(KNOWLEDGE_DIR))
        self.assertEqual(KnowledgeChunk.objects.count(), expected)

    def test_failure_keeps_the_old_index(self, mock_embed):
        KnowledgeChunk.objects.create(
            source='Alt', position=0, heading='Alt', content='Alt',
            embedding=unit_vector(0))
        mock_embed.side_effect = EmbeddingServiceError('down')
        with self.assertRaisesMessage(CommandError, 'down'):
            call_command('build_index', stdout=StringIO())
        self.assertEqual(KnowledgeChunk.objects.get().source, 'Alt')
