"""Tests for the clients of the embedding service, Laya and Claude."""

import json
from types import SimpleNamespace
from unittest.mock import create_autospec, patch

import anthropic
import httpx
from anthropic.resources.messages import Messages
from django.test import SimpleTestCase, override_settings

from assistant_app.embedding_client import (
    EmbeddingServiceError,
    embed_passages,
    embed_query,
)
from assistant_app.laya_client import (
    LayaServiceError,
    is_attack,
    score_question,
)
from assistant_app.llm_client import (
    ANSWER_FORMAT,
    SYSTEM_PROMPT,
    LlmServiceError,
    _client,
    answer_question,
)
from assistant_app.tests.helpers import ranked


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


def claude_response(data, stop_reason='end_turn'):
    """Return a fake Messages API response carrying the given JSON."""
    text = data if isinstance(data, str) else json.dumps(data)
    return SimpleNamespace(
        model='claude-haiku-4-5', stop_reason=stop_reason,
        _request_id='req_1',
        usage=SimpleNamespace(input_tokens=100, output_tokens=20),
        content=[SimpleNamespace(type='text', text=text)])


ANSWER = {'answer': ' Mit Django. ', 'answered': True, 'sources': [1]}


@override_settings(ANTHROPIC_API_KEY='test-key', ASSISTANT_LLM_PROFILE='haiku')
class LlmClientTests(SimpleTestCase):
    """Test the Claude client with the SDK mocked."""

    def setUp(self):
        """Mock the client with the signature of the installed SDK.

        A plain mock accepts any argument, so a parameter the SDK no longer
        knows would only fail against the real API.
        """
        messages = create_autospec(Messages, instance=True)
        client = patch('assistant_app.llm_client._client')
        self.mock_client = client.start()
        self.addCleanup(client.stop)
        self.mock_client.return_value.messages = messages
        self.create = messages.create

    def test_sends_profile_prompt_and_format(self):
        self.create.return_value = claude_response(ANSWER)
        answer_question('Wie <b>?', ranked('A', 'B'))
        kwargs = self.create.call_args.kwargs
        self.assertEqual(kwargs['model'], 'claude-haiku-4-5')
        self.assertEqual(kwargs['extra_body'], {'temperature': 0})
        self.assertNotIn('thinking', kwargs)
        self.assertEqual(kwargs['output_config'], {'format': ANSWER_FORMAT})
        self.assertEqual(kwargs['system'], SYSTEM_PROMPT)
        prompt = kwargs['messages'][0]['content']
        self.assertIn('<section id="2" heading="B">', prompt)
        self.assertIn('Wie &lt;b&gt;?', prompt)
        self.assertTrue(prompt.endswith('<language>German</language>'))

    def test_english_page_asks_for_english(self):
        self.create.return_value = claude_response(ANSWER)
        answer_question('Frage', ranked('A'), lang='en')
        prompt = self.create.call_args.kwargs['messages'][0]
        self.assertTrue(
            prompt['content'].endswith('<language>English</language>'))

    def test_thinking_profile_keeps_effort_and_format(self):
        self.create.return_value = claude_response(ANSWER)
        answer_question('Frage', ranked('A'), profile='sonnet-thinking')
        kwargs = self.create.call_args.kwargs
        self.assertEqual(kwargs['thinking'], {'type': 'adaptive'})
        self.assertEqual(kwargs['output_config'],
                         {'effort': 'low', 'format': ANSWER_FORMAT})
        self.assertNotIn('extra_body', kwargs)

    def test_haiku_5_5_profiles_send_no_temperature(self):
        self.create.return_value = claude_response(ANSWER)
        profiles = (('haiku-5-5', {'type': 'disabled'}),
                    ('haiku-5-5-thinking', {'type': 'adaptive'}))
        for profile, thinking in profiles:
            with self.subTest(profile=profile):
                answer_question('Frage', ranked('A'), profile=profile)
                kwargs = self.create.call_args.kwargs
                self.assertEqual(kwargs['model'], 'claude-haiku-5-5')
                self.assertEqual(kwargs['thinking'], thinking)
                self.assertNotIn('extra_body', kwargs)

    def test_skips_thinking_block_before_the_answer(self):
        response = claude_response(ANSWER)
        response.content.insert(
            0, SimpleNamespace(type='thinking', thinking='', signature='s'))
        self.create.return_value = response
        result = answer_question('Frage', ranked('A'))
        self.assertEqual(result['answer'], 'Mit Django.')

    def test_returns_answer_with_valid_sources_only(self):
        data = {'answer': 'Ja.', 'answered': True, 'sources': [2, 0, 5, 2]}
        self.create.return_value = claude_response(data)
        result = answer_question('Frage', ranked('A', 'B'))
        self.assertEqual(result, {
            'answer': 'Ja.', 'answered': True, 'sources': [2],
            'usage': {'input_tokens': 100, 'output_tokens': 20}})

    def test_refusal_returns_none(self):
        self.create.return_value = claude_response(
            '', stop_reason='refusal')
        self.assertIsNone(answer_question('Frage', ranked('A')))

    def test_unusable_answers_raise(self):
        cases = {
            'cut off': claude_response(ANSWER, stop_reason='max_tokens'),
            'no JSON': claude_response('oops'),
            'field missing': claude_response({'answer': 'Ja.'}),
            'answer not text': claude_response({**ANSWER, 'answer': 1}),
            'sources not a list': claude_response({**ANSWER, 'sources': 1}),
        }
        for label, response in cases.items():
            with self.subTest(label):
                self.create.return_value = response
                with self.assertRaises(LlmServiceError):
                    answer_question('Frage', ranked('A'))

    def test_sdk_errors_raise(self):
        self.create.side_effect = anthropic.AnthropicError('x')
        with self.assertRaisesMessage(LlmServiceError, 'not reachable'):
            answer_question('Frage', ranked('A'))

    @override_settings(ANTHROPIC_API_KEY='')
    def test_missing_key_raises_before_any_request(self):
        with self.assertRaisesMessage(LlmServiceError, 'ANTHROPIC_API_KEY'):
            answer_question('Frage', ranked('A'))
        self.mock_client.assert_not_called()

    def test_logs_usage_but_not_the_question(self):
        self.create.return_value = claude_response(ANSWER)
        with self.assertLogs('assistant_app.llm_client', 'INFO') as logs:
            answer_question('Geheime Frage', ranked('A'))
        self.assertIn('100 Tokens rein, 20 raus, Anfrage req_1',
                      logs.output[0])
        self.assertNotIn('Geheime Frage', logs.output[0])


@override_settings(ANTHROPIC_API_KEY='test-key')
class LlmClientFactoryTests(SimpleTestCase):
    """Test that the SDK client is built once with short timeouts."""

    def test_client_is_created_once(self):
        _client.cache_clear()
        self.addCleanup(_client.cache_clear)
        with patch('assistant_app.llm_client.anthropic.Anthropic') as sdk:
            self.assertIs(_client(), _client())
        sdk.assert_called_once_with(
            api_key='test-key', timeout=20, max_retries=1)
