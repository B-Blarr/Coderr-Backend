"""Tests for the assistant app: parsing, clients, index, API."""

import json
import os
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import httpx
from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from assistant_app.embedding_client import (
    EmbeddingServiceError,
    embed_passages,
    embed_query,
)
from assistant_app.knowledge_base import KnowledgeBaseError, read_sections
from assistant_app.laya_client import (
    LayaServiceError,
    is_attack,
    score_question,
)
from assistant_app.management.commands.evaluate_guard import DEFAULT_ATTACKS
from assistant_app.management.commands.evaluate_retrieval import (
    DEFAULT_QUESTIONS,
)
from assistant_app.models import KnowledgeChunk
from core.settings import env_probability

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / 'knowledge'


def unit_vector(axis):
    """Return a 768-dimensional vector that points along one axis."""
    vector = [0.0] * 768
    vector[axis] = 1.0
    return vector


def ranked(*headings):
    """Return unsaved chunks in the given order, best match first."""
    chunks = []
    for rank, heading in enumerate(headings, start=1):
        chunk = KnowledgeChunk(heading=heading)
        chunk.distance = rank / 10
        chunks.append(chunk)
    return chunks


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


@patch('assistant_app.embedding_client.httpx.post')
class EmbeddingClientTests(SimpleTestCase):
    """Test the HTTP client with the embedding service mocked."""

    def test_query_is_sent_as_query(self, mock_post):
        mock_post.return_value = httpx.Response(
            200, json={'vectors': [[0.1, 0.2]]})
        self.assertEqual(embed_query('Frage'), [0.1, 0.2])
        self.assertEqual(
            mock_post.call_args.kwargs['json'],
            {'kind': 'query', 'texts': ['Frage']},
        )

    def test_passages_are_sent_in_batches_of_64(self, mock_post):
        mock_post.side_effect = lambda url, json, timeout: httpx.Response(
            200, json={'vectors': [[1.0]] * len(json['texts'])})
        vectors = embed_passages([f"text {i}" for i in range(65)])
        self.assertEqual(len(vectors), 65)
        batch_sizes = [
            len(call.kwargs['json']['texts'])
            for call in mock_post.call_args_list
        ]
        self.assertEqual(batch_sizes, [64, 1])

    def test_no_request_without_passages(self, mock_post):
        self.assertEqual(embed_passages([]), [])
        mock_post.assert_not_called()

    def test_unreachable_service_raises(self, mock_post):
        mock_post.side_effect = httpx.ConnectError('refused')
        with self.assertRaisesMessage(EmbeddingServiceError, 'ConnectError'):
            embed_query('Frage')

    def test_error_status_raises_with_body(self, mock_post):
        mock_post.return_value = httpx.Response(422, text='too long')
        with self.assertRaisesMessage(EmbeddingServiceError, '422: too long'):
            embed_query('Frage')


def laya_answer(jailbreak):
    """Return a Laya response body with the given jailbreak score."""
    return {'answers': {'jailbreak': {'type': 'noul', 'noul': jailbreak}}}


@patch('assistant_app.laya_client.httpx.post')
class LayaClientTests(SimpleTestCase):
    """Test the HTTP client with the Laya service mocked."""

    def test_question_is_sent_as_prompt(self, mock_post):
        mock_post.return_value = httpx.Response(
            200, json=laya_answer(0.98))
        scores = score_question('Frage')
        self.assertEqual(scores, {'jailbreak': 0.98})
        body = mock_post.call_args.kwargs['json']
        self.assertEqual(body['model'], 'multilingual')
        self.assertEqual(body['state'], {'prompt': 'Frage'})
        self.assertEqual(set(body['questions']), set(scores))

    def test_unreachable_or_slow_service_raises(self, mock_post):
        for error in (httpx.ConnectError('refused'), httpx.ReadTimeout('')):
            with self.subTest(type(error).__name__):
                mock_post.side_effect = error
                with self.assertRaisesMessage(
                        LayaServiceError, type(error).__name__):
                    score_question('Frage')

    def test_error_status_raises_with_body(self, mock_post):
        mock_post.return_value = httpx.Response(422, text='bad question')
        with self.assertRaisesMessage(LayaServiceError, '422: bad question'):
            score_question('Frage')

    def test_unusable_answers_raise(self, mock_post):
        cases = {
            'no JSON': httpx.Response(200, text='oops'),
            'no answers': httpx.Response(200, json={}),
            'score missing': httpx.Response(
                200, json={'answers': {'other': {'noul': 0.0}}}),
            'score is null': httpx.Response(200, json=laya_answer(None)),
            'score is text': httpx.Response(200, json=laya_answer('x')),
            'score above 1': httpx.Response(200, json=laya_answer(1.5)),
            'score below 0': httpx.Response(200, json=laya_answer(-0.1)),
            'score is NaN': httpx.Response(
                200, text='{"answers": {"jailbreak": {"noul": NaN}}}'),

        }
        for label, response in cases.items():
            with self.subTest(label):
                mock_post.return_value = response
                with self.assertRaises(LayaServiceError):
                    score_question('Frage')


@override_settings(LAYA_THRESHOLD=0.8)
class IsAttackTests(SimpleTestCase):
    """Test the threshold decision without any service."""

    def test_score_at_the_threshold_blocks(self):
        cases = [(0.0, False), (0.79, False), (0.8, True), (0.98, True)]
        for score, expected in cases:
            with self.subTest(score=score):
                self.assertIs(is_attack({'jailbreak': score}), expected)


class EnvProbabilityTests(SimpleTestCase):
    """Test the helper that reads LAYA_THRESHOLD at startup."""

    def read(self, raw):
        with patch.dict(os.environ, {'TEST_PROBABILITY': raw}):
            return env_probability('TEST_PROBABILITY', '0.5')

    def test_reads_values_up_to_1(self):
        self.assertEqual(self.read('0.7'), 0.7)
        self.assertEqual(self.read('1'), 1.0)

    def test_uses_default_when_unset(self):
        self.assertEqual(env_probability('TEST_PROBABILITY_UNSET', '0.5'), 0.5)

    def test_rejects_invalid_values(self):
        for raw in ('0', '-0.1', '1.5', '5', 'nan', 'inf', 'abc', ''):
            with self.subTest(raw=raw):
                with self.assertRaisesMessage(ValueError, 'TEST_PROBABILITY'):
                    self.read(raw)


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


@override_settings(ASSISTANT_ENABLED=True)
@patch('assistant_app.retrieval.embed_query')
class AssistantViewTests(APITestCase):
    """Test POST /api/assistant/ with the embedding service mocked."""

    def setUp(self):
        self.url = reverse('assistant')
        for axis in range(7):
            KnowledgeChunk.objects.create(
                source='Quelle', position=axis, heading=f"Heading {axis}",
                content='Text', embedding=unit_vector(axis))

    def ask(self, question='Wie deployt Benjamin?', **extra):
        return self.client.post(
            self.url, {'question': question}, format='json', **extra)

    def test_returns_closest_sections_first(self, mock_embed):
        mock_embed.return_value = unit_vector(3)
        response = self.ask()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0]['heading'], 'Heading 3')
        self.assertEqual(results[0]['similarity'], 1.0)
        self.assertEqual(results[1]['similarity'], 0.0)
        self.assertEqual(
            list(results[0]), ['source', 'heading', 'content', 'similarity'])

    def test_invalid_questions_return_400(self, mock_embed):
        for question in ['   ', 'a' * 501]:
            with self.subTest(length=len(question)):
                response = self.ask(question)
                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_embed.assert_not_called()

    def test_stale_token_header_is_ignored(self, mock_embed):
        mock_embed.return_value = unit_vector(0)
        response = self.ask(HTTP_AUTHORIZATION='Token invalid')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_service_failure_returns_503(self, mock_embed):
        mock_embed.side_effect = EmbeddingServiceError('down')
        with self.assertLogs('assistant_app.api.views', 'ERROR'):
            response = self.ask()
        self.assertEqual(
            response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @override_settings(ASSISTANT_ENABLED=False)
    def test_switched_off_returns_503(self, mock_embed):
        response = self.ask()
        self.assertEqual(
            response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        mock_embed.assert_not_called()


@patch('assistant_app.management.commands.evaluate_retrieval.search')
class EvaluateRetrievalTests(TestCase):
    """Test the evaluation report with the search mocked."""

    def setUp(self):
        for position, heading in enumerate(['Deploy', 'Git', 'Team']):
            KnowledgeChunk.objects.create(
                source='Quelle', position=position, heading=heading,
                content='Text', embedding=unit_vector(position))
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.questions = Path(temp_dir.name) / 'questions.json'

    def evaluate(self, cases):
        self.questions.write_text(json.dumps(cases), encoding='utf-8')
        output = StringIO()
        call_command(
            'evaluate_retrieval', questions=self.questions, stdout=output)
        return output.getvalue()

    def test_reports_hits_misses_and_off_topic(self, mock_search):
        mock_search.side_effect = [
            ranked('Team', 'Deploy', 'Git'),
            ranked('Team', 'Git', 'Other', 'Deploy'),
            ranked('Git', 'Team'),
        ]
        output = self.evaluate([
            {'question': 'Wie deployt er?', 'expected': ['Deploy']},
            {'question': 'Und wie genau?', 'expected': ['Deploy']},
            {'question': 'Lasagne?', 'expected': []},
        ])
        self.assertIn('HIT  2 0.900  Wie deployt er?', output)
        self.assertIn('MISS 4 0.900  Und wie genau?', output)
        self.assertIn('OFF  - 0.900  Lasagne?', output)
        self.assertIn('best: Git', output)
        self.assertIn('In top 3: 1 of 2', output)

    def test_rejects_unknown_headings(self, mock_search):
        cases = [
            {'question': 'Frage', 'expected': ['Tippfehler']},
            {'question': 'Lasagne?', 'expected': []},
        ]
        with self.assertRaisesMessage(CommandError, 'Tippfehler'):
            self.evaluate(cases)

    def test_rejects_empty_index(self, mock_search):
        KnowledgeChunk.objects.all().delete()
        cases = [
            {'question': 'Frage', 'expected': ['Deploy']},
            {'question': 'Lasagne?', 'expected': []},
        ]
        with self.assertRaisesMessage(CommandError, 'build_index'):
            self.evaluate(cases)

    def test_needs_questions_on_and_off_topic(self, mock_search):
        cases = [{'question': 'Frage', 'expected': ['Deploy']}]
        with self.assertRaisesMessage(CommandError, 'both needed'):
            self.evaluate(cases)

    def test_service_failure_is_reported(self, mock_search):
        mock_search.side_effect = EmbeddingServiceError('down')
        cases = [
            {'question': 'Frage', 'expected': ['Deploy']},
            {'question': 'Lasagne?', 'expected': []},
        ]
        with self.assertRaisesMessage(CommandError, 'down'):
            self.evaluate(cases)


@override_settings(LAYA_THRESHOLD=0.8)
@patch('assistant_app.management.commands.evaluate_guard.score_question')
class EvaluateGuardTests(SimpleTestCase):
    """Test the filter report with the Laya service mocked."""

    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.questions = Path(temp_dir.name) / 'questions.json'
        self.attacks = Path(temp_dir.name) / 'attacks.json'

    def evaluate(self, questions, attacks):
        self.questions.write_text(json.dumps(questions), encoding='utf-8')
        self.attacks.write_text(json.dumps(attacks), encoding='utf-8')
        output = StringIO()
        call_command('evaluate_guard', questions=self.questions,
                     attacks=self.attacks, stdout=output)
        return output.getvalue()

    def test_reports_all_four_outcomes(self, mock_score):
        scores = {'Frage': 0.1, 'KI?': 0.85, 'Laut': 0.99, 'Leise': 0.02}
        mock_score.side_effect = lambda text: {'jailbreak': scores[text]}
        output = self.evaluate([
            {'question': 'Frage', 'expected': ['Deploy']},
            {'question': 'KI?', 'expected': ['KI']},
            {'question': 'Lasagne?', 'expected': []},
        ], ['Laut', 'Leise'])
        self.assertIn('PASS  0.100  Frage', output)
        self.assertIn('BLOCK 0.850  KI?', output)
        self.assertIn('CATCH 0.990  Laut', output)
        self.assertIn('MISS  0.020  Leise', output)
        self.assertNotIn('Lasagne?', output)
        self.assertIn('Attacks caught:    1 of 2', output)
        self.assertIn('Questions blocked: 1 of 2', output)
        self.assertIn('Highest score on topic: 0.850 (threshold 0.8)', output)

    def test_needs_questions_on_topic_and_attacks(self, mock_score):
        cases = {
            'no attacks': ([{'question': 'Frage', 'expected': ['A']}], []),
            'only off topic': ([{'question': 'Frage', 'expected': []}], ['X']),
        }
        for label, (questions, attacks) in cases.items():
            with self.subTest(label):
                with self.assertRaisesMessage(CommandError, 'are needed'):
                    self.evaluate(questions, attacks)
        mock_score.assert_not_called()

    def test_service_failure_is_reported(self, mock_score):
        mock_score.side_effect = LayaServiceError('down')
        questions = [{'question': 'Frage', 'expected': ['A']}]
        with self.assertRaisesMessage(CommandError, 'down'):
            self.evaluate(questions, ['X'])

    def test_shipped_attacks_are_texts(self, mock_score):
        attacks = json.loads(DEFAULT_ATTACKS.read_text(encoding='utf-8'))
        self.assertGreater(len(attacks), 0)
        for attack in attacks:
            with self.subTest(attack=attack):
                self.assertIsInstance(attack, str)
                self.assertTrue(attack.strip())
