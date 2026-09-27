"""Management command that measures the Laya filter on fixed texts."""

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from assistant_app.laya_client import (
    LayaServiceError,
    is_attack,
    score_question,
)

APP_DIR = Path(__file__).resolve().parents[2]
DEFAULT_QUESTIONS = APP_DIR / 'retrieval_questions.json'
DEFAULT_ATTACKS = APP_DIR / 'guard_attacks.json'
VERDICTS = {
    (False, False): 'PASS ',
    (False, True): 'BLOCK',
    (True, True): 'CATCH',
    (True, False): 'MISS ',
}


class Command(BaseCommand):
    """Sends genuine questions and attacks through Laya.

    No question on topic should be blocked, and as many attacks as
    possible should be. Off-topic questions from the retrieval list are
    skipped: blocking them does no harm, so they say nothing about the
    threshold.
    """

    help = "Measure the Laya input filter with fixed questions and attacks."

    def add_arguments(self, parser):
        """Allow different files, e.g. for experiments."""
        parser.add_argument(
            '--questions', type=Path, default=DEFAULT_QUESTIONS)
        parser.add_argument('--attacks', type=Path, default=DEFAULT_ATTACKS)

    def handle(self, *args, **options):
        """Score every text and print one line each plus a summary."""
        questions = self._load_questions(options['questions'])
        attacks = json.loads(options['attacks'].read_text(encoding='utf-8'))
        if not questions or not attacks:
            raise CommandError("Questions on topic and attacks are needed.")
        try:
            rows = ([self._evaluate(text, False) for text in questions]
                    + [self._evaluate(text, True) for text in attacks])
        except LayaServiceError as error:
            raise CommandError(error) from error
        for row in rows:
            self.stdout.write(self._format(row))
        self._summarize(rows)

    def _load_questions(self, path):
        """Return the questions on topic from the retrieval list."""
        cases = json.loads(path.read_text(encoding='utf-8'))
        return [case['question'] for case in cases if case['expected']]

    def _evaluate(self, text, attack):
        """Score one text and record whether Laya blocks it."""
        scores = score_question(text)
        return {
            'text': text,
            'attack': attack,
            'score': max(scores.values()),
            'blocked': is_attack(scores),
        }

    def _format(self, row):
        """Return the report line for one text."""
        verdict = VERDICTS[(row['attack'], row['blocked'])]
        return f"{verdict} {row['score']:.3f}  {row['text']}"

    def _summarize(self, rows):
        """Print caught attacks, blocked questions and the margin."""
        attacks = [row for row in rows if row['attack']]
        questions = [row for row in rows if not row['attack']]
        caught = sum(row['blocked'] for row in attacks)
        blocked = sum(row['blocked'] for row in questions)
        highest = max(row['score'] for row in questions)
        self.stdout.write(
            f"\nAttacks caught:    {caught} of {len(attacks)}\n"
            f"Questions blocked: {blocked} of {len(questions)}\n"
            f"Highest score on topic: {highest:.3f} "
            f"(threshold {settings.LAYA_THRESHOLD})"
        )
