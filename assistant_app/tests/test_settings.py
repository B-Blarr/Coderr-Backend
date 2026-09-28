"""Tests for the assistant settings and their system check."""

import os
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from assistant_app.checks import check_llm_settings
from core.settings import env_probability


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


class LlmSettingsCheckTests(SimpleTestCase):
    """Test the system check for the language model settings."""

    def message_ids(self):
        return [message.id for message in check_llm_settings(None)]

    @override_settings(ASSISTANT_LLM_PROFILE='gpt', ASSISTANT_ENABLED=False)
    def test_unknown_profile_is_an_error(self):
        self.assertEqual(self.message_ids(), ['assistant_app.E001'])

    @override_settings(ASSISTANT_ENABLED=True, ANTHROPIC_API_KEY='')
    def test_enabled_assistant_needs_a_key(self):
        self.assertEqual(self.message_ids(), ['assistant_app.W001'])

    @override_settings(ASSISTANT_ENABLED=False, ANTHROPIC_API_KEY='')
    def test_switched_off_assistant_needs_no_key(self):
        self.assertEqual(self.message_ids(), [])
