"""Recognizes messages that only greet, thank or say goodbye."""

import re

GREETINGS = frozenset({
    'hallo', 'halo', 'hi', 'hey', 'moin', 'servus', 'gude', 'morgen',
    'guten morgen', 'guten tag', 'guten abend', 'hello', 'good morning',
    'danke', 'thanks', 'tschüss', 'bye',
})


def is_greeting(text):
    """Tell whether the whole message is one of the known greetings.

    Case, punctuation and emojis are ignored. A greeting followed by a
    real question is not a greeting and goes the normal way.
    """
    words = re.findall(r'\w+', text.casefold())
    return ' '.join(words) in GREETINGS
