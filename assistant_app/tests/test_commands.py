"""Tests for the evaluate_retrieval, _guard and _answers commands."""

import json
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase, override_settings

from assistant_app.embedding_client import EmbeddingServiceError
from assistant_app.laya_client import LayaServiceError
from assistant_app.llm_client import LANGUAGES, LlmServiceError
from assistant_app.management.commands.evaluate_answers import (
    DEFAULT_QUESTIONS as ANSWER_QUESTIONS,
)
from assistant_app.management.commands.evaluate_guard import DEFAULT_ATTACKS
from assistant_app.models import KnowledgeChunk
from assistant_app.tests.helpers import ranked, unit_vector


@override_settings(ASSISTANT_MIN_SIMILARITY=0.85)
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

    def test_counts_questions_below_the_threshold(self, mock_search):
        weak = ranked('Git')
        weak[0].distance = 0.3
        mock_search.side_effect = [ranked('Deploy'), weak]
        output = self.evaluate([
            {'question': 'Wie deployt er?', 'expected': ['Deploy']},
            {'question': 'Lasagne?', 'expected': []},
        ])
        self.assertIn(
            'Below threshold 0.85: 0 of 1 on topic, 1 of 1 off topic', output)

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


def fake_answer(answered):
    """Return a Claude result as answer_question delivers it."""
    return {'answer': 'Mit Django.', 'answered': answered, 'sources': [1],
            'usage': {'input_tokens': 1000, 'output_tokens': 100}}


@override_settings(ASSISTANT_MIN_SIMILARITY=0.85)
@patch('assistant_app.management.commands.evaluate_answers.answer_question')
@patch('assistant_app.management.commands.evaluate_answers.search')
class EvaluateAnswersTests(SimpleTestCase):
    """Test the profile comparison with search and Claude mocked."""

    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.questions = Path(temp_dir.name) / 'questions.json'

    def evaluate(self, cases, run=True):
        self.questions.write_text(json.dumps(cases), encoding='utf-8')
        output = StringIO()
        call_command('evaluate_answers', questions=self.questions,
                     profiles=['haiku'], run=run, stdout=output)
        return output.getvalue()

    def search_results(self):
        weak = ranked('Weak')
        weak[0].distance = 0.3
        return {'Django?': ranked('A'), 'Gehalt?': ranked('B'),
                'Everest?': weak, 'Pokedex?': ranked('C')}

    def test_preview_sends_nothing(self, mock_search, mock_answer):
        mock_search.side_effect = self.search_results().get
        output = self.evaluate([
            {'question': 'Django?', 'expect': 'answer'},
            {'question': 'Everest?', 'expect': 'decline'},
        ], run=False)
        self.assertIn('1 of 2 questions pass the threshold', output)
        self.assertIn('about 0.3 cents', output)
        mock_answer.assert_not_called()

    def test_run_judges_every_case(self, mock_search, mock_answer):
        mock_search.side_effect = self.search_results().get
        results = {'Django?': fake_answer(True), 'Gehalt?': fake_answer(False),
                   'Pokedex?': None}
        mock_answer.side_effect = lambda question, *_, **__: results[question]
        output = self.evaluate([
            {'question': 'Django?', 'expect': 'answer'},
            {'question': 'Gehalt?', 'lang': 'en', 'expect': 'decline'},
            {'question': 'Everest?', 'expect': 'resist'},
            {'question': 'Pokedex?', 'expect': 'answer'},
        ])
        self.assertIn('[OK  ] answer: answered, 0.15 cents', output)
        self.assertIn('[OK  ] decline: not answered, 0.15 cents', output)
        self.assertIn('[OK  ] resist: OFF TOPIC, 0.00 cents, 0.0 s', output)
        self.assertIn('[FAIL] answer: REFUSED', output)
        self.assertIn('A: Mit Django.', output)
        self.assertIn('Q (en): Gehalt?', output)
        self.assertIn('haiku: 3 of 4 as expected, 0.30 cents', output)
        self.assertEqual(mock_answer.call_count, 3)
        languages = [call.kwargs for call in mock_answer.call_args_list]
        self.assertEqual(languages, [
            {'lang': 'de', 'profile': 'haiku'},
            {'lang': 'en', 'profile': 'haiku'},
            {'lang': 'de', 'profile': 'haiku'},
        ])

    def test_rejects_bad_question_files(self, mock_search, mock_answer):
        cases = {
            'empty': [],
            "['maybe']": [{'question': 'Q', 'expect': 'maybe'}],
            "['fr']": [{'question': 'Q', 'lang': 'fr', 'expect': 'answer'}],
        }
        for message, questions in cases.items():
            with self.subTest(message):
                with self.assertRaisesMessage(CommandError, message):
                    self.evaluate(questions)

    def test_service_failures_are_reported(self, mock_search, mock_answer):
        cases = [{'question': 'Django?', 'expect': 'answer'}]
        mock_search.side_effect = EmbeddingServiceError('embedding down')
        with self.assertRaisesMessage(CommandError, 'embedding down'):
            self.evaluate(cases)
        mock_search.side_effect = self.search_results().get
        mock_answer.side_effect = LlmServiceError('claude down')
        with self.assertRaisesMessage(CommandError, 'claude down'):
            self.evaluate(cases)

    def test_shipped_questions_cover_every_expectation(self, *mocks):
        cases = json.loads(
            ANSWER_QUESTIONS.read_text(encoding='utf-8'))
        self.assertEqual({case['expect'] for case in cases},
                         {'answer', 'decline', 'resist'})
        for case in cases:
            with self.subTest(case['question']):
                self.assertTrue(case['question'].strip())
                self.assertIn(case['lang'], LANGUAGES)
