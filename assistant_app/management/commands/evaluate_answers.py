"""Management command that compares the LLM profiles on fixed questions."""

import json
import time
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from assistant_app.embedding_client import EmbeddingServiceError
from assistant_app.llm_client import PROFILES, LlmServiceError, answer_question
from assistant_app.retrieval import keep_relevant, search

DEFAULT_QUESTIONS = (
    Path(__file__).resolve().parents[2] / 'answer_questions.json'
)
# Dollars per million input and output tokens, from the Claude docs.
PRICES = {'claude-haiku-4-5': (1.0, 5.0), 'claude-sonnet-5': (2.0, 10.0)}
# Rough tokens per question, measured once; thinking may add more.
ESTIMATED_TOKENS = (1500, 300)
EXPECTED_ANSWERED = {'answer': True, 'decline': False, 'resist': False}


class Command(BaseCommand):
    """Sends fixed questions through search and Claude, once per profile.

    With --run every question that passes the similarity threshold costs
    real money, so without it the command only shows what it would send.
    Laya is left out on purpose: this measures what gets past it. Only
    the answered flag is checked automatically; tone, language and false
    claims need a human reader.
    """

    help = "Compare the LLM profiles on fixed questions (costs money)."

    def add_arguments(self, parser):
        """Pick the question file and profiles; --run spends money."""
        parser.add_argument(
            '--questions', type=Path, default=DEFAULT_QUESTIONS)
        parser.add_argument(
            '--profiles', nargs='+', choices=list(PROFILES),
            default=list(PROFILES))
        parser.add_argument(
            '--run', action='store_true', help="Really call Claude.")

    def handle(self, *args, **options):
        """Search every question once, then preview or run each profile."""
        cases = self._load_cases(options['questions'])
        try:
            contexts = [(case, keep_relevant(search(case['question'])))
                        for case in cases]
        except EmbeddingServiceError as error:
            raise CommandError(error) from error
        if not options['run']:
            return self._preview(contexts, options['profiles'])
        for profile in options['profiles']:
            self._evaluate(profile, contexts)

    def _load_cases(self, path):
        """Read the questions and reject unknown expectations."""
        cases = json.loads(path.read_text(encoding='utf-8'))
        if not cases:
            raise CommandError("The question file is empty.")
        unknown = {c['expect'] for c in cases} - set(EXPECTED_ANSWERED)
        if unknown:
            raise CommandError(f"Unknown expectations: {sorted(unknown)}")
        return cases

    def _preview(self, contexts, profiles):
        """Show how many questions would reach Claude and a rough cost."""
        calls = sum(1 for _, chunks in contexts if chunks)
        cents = sum(_cents(p, *ESTIMATED_TOKENS) for p in profiles) * calls
        self.stdout.write(
            f"{calls} of {len(contexts)} questions pass the threshold and "
            f"would reach Claude, for {', '.join(profiles)}.\n"
            f"Estimated cost: about {cents:.1f} cents. "
            f"Add --run to send them.")

    def _evaluate(self, profile, contexts):
        """Ask every question with one profile and print a summary."""
        self.stdout.write(f"\n===== {profile} =====")
        rows = [self._ask(profile, case, chunks) for case, chunks in contexts]
        passed = sum(row['passed'] for row in rows)
        cents = sum(row['cents'] for row in rows)
        timed = [row['seconds'] for row in rows if row['seconds']]
        average = sum(timed) / len(timed) if timed else 0
        self.stdout.write(
            f"\n{profile}: {passed} of {len(rows)} as expected, "
            f"{cents:.2f} cents, {average:.1f} s per answer")

    def _ask(self, profile, case, chunks):
        """Ask one question, print the result and return its numbers."""
        start = time.perf_counter()
        try:
            result = (answer_question(case['question'], chunks, profile)
                      if chunks else None)
        except LlmServiceError as error:
            raise CommandError(error) from error
        row = _row(profile, case, chunks, result)
        row['seconds'] = time.perf_counter() - start if chunks else 0
        self.stdout.write(_format(case, row, result))
        return row


def _cents(profile, input_tokens, output_tokens):
    """Return the cost of one request in cents."""
    input_price, output_price = PRICES[PROFILES[profile]['model']]
    dollars = (input_tokens * input_price
               + output_tokens * output_price) / 1_000_000
    return dollars * 100


def _row(profile, case, chunks, result):
    """Judge one result against its expectation."""
    answered = bool(result and result['answered'])
    usage = result['usage'] if result else {}
    cents = _cents(profile, usage['input_tokens'],
                   usage['output_tokens']) if usage else 0
    if not chunks:
        status = 'OFF TOPIC'
    elif result is None:
        status = 'REFUSED'
    else:
        status = 'answered' if answered else 'not answered'
    passed = answered == EXPECTED_ANSWERED[case['expect']]
    return {'status': status, 'passed': passed, 'cents': cents}


def _format(case, row, result):
    """Return the report lines for one question."""
    verdict = 'OK  ' if row['passed'] else 'FAIL'
    line = (f"\n[{verdict}] {case['expect']}: {row['status']}, "
            f"{row['cents']:.2f} cents, {row['seconds']:.1f} s\n"
            f"  Q: {case['question']}")
    if result:
        line += (f"\n  A: {result['answer']}"
                 f"\n  sources: {result['sources']}")
    return line
