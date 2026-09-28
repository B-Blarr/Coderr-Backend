"""Management command that measures retrieval quality on fixed questions."""

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from assistant_app.embedding_client import EmbeddingServiceError
from assistant_app.models import KnowledgeChunk
from assistant_app.retrieval import search

DEFAULT_QUESTIONS = (
    Path(__file__).resolve().parents[2] / 'retrieval_questions.json'
)
TOP_K = 3


class Command(BaseCommand):
    """Checks every question against the sections it should find.

    A question with expected headings must find one of them among the
    first three results. A question without expected headings is off
    topic; for those only the best score counts, because they decide
    the similarity threshold of the next stage.
    """

    help = "Measure retrieval quality with a fixed list of questions."

    def add_arguments(self, parser):
        """Allow a different question file, e.g. for experiments."""
        parser.add_argument(
            '--questions', type=Path, default=DEFAULT_QUESTIONS)

    def handle(self, *args, **options):
        """Run all questions and print one line each plus a summary."""
        cases = self._load_cases(options['questions'])
        try:
            rows = [self._evaluate(case) for case in cases]
        except EmbeddingServiceError as error:
            raise CommandError(error) from error
        for row in rows:
            self.stdout.write(self._format(row))
        self._summarize(rows)

    def _load_cases(self, path):
        """Read the questions, which must cover both on and off topic."""
        cases = json.loads(path.read_text(encoding='utf-8'))
        if {bool(case['expected']) for case in cases} != {True, False}:
            raise CommandError("Questions on and off topic are both needed.")
        self._check_headings(cases)
        return cases

    def _check_headings(self, cases):
        """Reject expected headings that do not exist in the index."""
        known = set(KnowledgeChunk.objects.values_list('heading', flat=True))
        if not known:
            raise CommandError("The index is empty, run build_index first.")
        unknown = {h for case in cases for h in case['expected']} - known
        if unknown:
            raise CommandError(f"Unknown headings: {sorted(unknown)}")

    def _evaluate(self, case):
        """Search one question and find the rank of an expected heading."""
        chunks = search(case['question'])
        headings = [chunk.heading for chunk in chunks]
        ranks = [rank for rank, heading in enumerate(headings, start=1)
                 if heading in case['expected']]
        return {
            'question': case['question'],
            'on_topic': bool(case['expected']),
            'rank': ranks[0] if ranks else None,
            'best_score': 1 - chunks[0].distance,
            'best_heading': headings[0],
        }

    def _format(self, row):
        """Return the report line for one question."""
        if not row['on_topic']:
            verdict = 'OFF '
        elif row['rank'] and row['rank'] <= TOP_K:
            verdict = 'HIT '
        else:
            verdict = 'MISS'
        rank = row['rank'] or '-'
        line = f"{verdict} {rank} {row['best_score']:.3f}  {row['question']}"
        if verdict != 'HIT ':
            line += f"\n             best: {row['best_heading']}"
        return line

    def _summarize(self, rows):
        """Print the hit rate and the best scores on and off topic."""
        on_topic = [row for row in rows if row['on_topic']]
        off_topic = [row for row in rows if not row['on_topic']]
        hits = [row for row in on_topic
                if row['rank'] and row['rank'] <= TOP_K]
        lowest_on = min(row['best_score'] for row in on_topic)
        highest_off = max(row['best_score'] for row in off_topic)
        self.stdout.write(
            f"\nIn top {TOP_K}: {len(hits)} of {len(on_topic)}\n"
            f"Lowest best score on topic:   {lowest_on:.3f}\n"
            f"Highest best score off topic: {highest_off:.3f}\n"
            f"{self._below_threshold(on_topic, off_topic)}"
        )

    def _below_threshold(self, on_topic, off_topic):
        """Count the questions the similarity threshold would stop."""
        threshold = settings.ASSISTANT_MIN_SIMILARITY
        below_on = sum(row['best_score'] < threshold for row in on_topic)
        below_off = sum(row['best_score'] < threshold for row in off_topic)
        return (
            f"Below threshold {threshold}: {below_on} of {len(on_topic)} "
            f"on topic, {below_off} of {len(off_topic)} off topic"
        )
