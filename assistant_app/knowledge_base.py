"""Reads the Markdown knowledge base and splits it into sections."""

import re
from dataclasses import dataclass

FRONTMATTER = re.compile(r'\A---\n(.*?)\n---(?:\n|\Z)', re.DOTALL)
HEADING = re.compile(r'^## (.+)$', re.MULTILINE)


class KnowledgeBaseError(Exception):
    """A knowledge file does not follow the expected format."""


@dataclass(frozen=True)
class Section:
    """One ``##`` section of a knowledge file."""

    source: str
    position: int
    heading: str
    content: str

    @property
    def passage(self):
        """Return the text that is sent to the embedding model."""
        return f"{self.heading}\n\n{self.content}"


def read_sections(directory):
    """Return the sections of all knowledge files, sorted by file name."""
    paths = sorted(directory.glob('*.md'))
    if not paths:
        raise KnowledgeBaseError(f"No knowledge files in {directory}.")
    return [section for path in paths for section in parse_file(path)]


def parse_file(path):
    """Split one knowledge file into its ``##`` sections."""
    text = path.read_text(encoding='utf-8-sig')
    match = FRONTMATTER.match(text)
    if not match:
        raise KnowledgeBaseError(f"{path.name}: frontmatter is missing.")
    source = _frontmatter_value(match.group(1), 'quelle', path)
    return _split_sections(path, source, text[match.end():])


def _frontmatter_value(block, key, path):
    """Return one value from a frontmatter block of 'key: value' lines."""
    for line in block.splitlines():
        name, _, value = line.partition(':')
        if name.strip() == key and value.strip():
            return value.strip()
    raise KnowledgeBaseError(f"{path.name}: '{key}' is missing.")


def _split_sections(path, source, body):
    """Cut the text below the frontmatter at every ``##`` heading."""
    parts = HEADING.split(body)
    if parts[0].strip():
        raise KnowledgeBaseError(
            f"{path.name}: text before the first '## ' heading."
        )
    if len(parts) == 1:
        raise KnowledgeBaseError(f"{path.name}: no '## ' heading found.")
    pairs = zip(parts[1::2], parts[2::2])
    return [
        _section(path, source, position, heading, text)
        for position, (heading, text) in enumerate(pairs)
    ]


def _section(path, source, position, heading, text):
    """Build one section and reject a heading without text below it."""
    if not text.strip():
        raise KnowledgeBaseError(
            f"{path.name}: section '{heading}' is empty."
        )
    return Section(source, position, heading.strip(), text.strip())
