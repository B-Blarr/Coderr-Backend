"""Recognizes messages that need no search: small talk and nonsense."""

import re

SMALL_TALK = {
    'greeting': frozenset({
        'hallo', 'halo', 'hi', 'hey', 'moin', 'moin moin', 'servus', 'gude',
        'morgen', 'guten morgen', 'guten tag', 'guten abend',
        'hallo zusammen', 'hello', 'good morning', 'good afternoon',
        'good evening',
    }),
    'thanks': frozenset({
        'danke', 'danke schön', 'dankeschön', 'danke sehr', 'danke dir',
        'vielen dank', 'besten dank', 'thanks', 'thanks a lot', 'thank you',
        'thank you very much', 'thx', 'merci',
    }),
    'farewell': frozenset({
        'tschüss', 'tschüs', 'tschau', 'ciao', 'auf wiedersehen', 'bis dann',
        'bis bald', 'bis später', 'bye', 'bye bye', 'goodbye', 'good bye',
        'see you',
    }),
}

MIN_NONSENSE_LENGTH = 5
MAX_NONSENSE_LETTERS = 2


def quick_reply_kind(text):
    """Return the kind of a message that needs no search, or None.

    Obvious nonsense is ``unclear``, pure small talk is ``greeting``,
    ``thanks`` or ``farewell``. Every other message goes the normal way.
    """
    if is_unclear(text):
        return 'unclear'
    return small_talk_kind(text)


def small_talk_kind(text):
    """Return the small talk kind of the whole message, or None.

    Case, punctuation and emojis are ignored. Small talk followed by a
    real question is not small talk and goes the normal way.
    """
    message = ' '.join(re.findall(r'\w+', text.casefold()))
    return next(
        (kind for kind, phrases in SMALL_TALK.items() if message in phrases),
        None,
    )


def is_unclear(text):
    """Tell whether the message is obvious nonsense.

    That is a message without any letter, such as "???" or "123", or one
    of at least five letters that uses no more than two different ones,
    such as "hhhhhhh" or "GHGHGH". The limits are kept tight on purpose:
    short words like "CSS" or "PHP" are real questions.
    """
    letters = [char for char in text.casefold() if char.isalpha()]
    if not letters:
        return True
    return (len(letters) >= MIN_NONSENSE_LENGTH
            and len(set(letters)) <= MAX_NONSENSE_LETTERS)
