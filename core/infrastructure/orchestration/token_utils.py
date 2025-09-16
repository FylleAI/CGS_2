"""Utility helpers for lightweight token estimation and truncation.

These helpers intentionally avoid external tokenizer dependencies so that
unit tests can run without optional packages such as ``tiktoken``.
The implementation relies on a simple regular-expression based approach
that preserves whitespace while counting tokens in a deterministic way.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


_TOKEN_PATTERN = re.compile(r"\S+\s*")


@dataclass
class TokenSlice:
    """Representation of a token span within a string."""

    text: str
    end: int


class SimpleTokenizer:
    """Very small helper used to approximate token counts.

    The goal is not to perfectly match any provider specific tokenizer but to
    obtain a stable metric for budgeting logic. Each "token" corresponds to a
    contiguous block of non-whitespace characters along with their trailing
    whitespace. This makes truncation operations preserve the original layout
    as much as possible.
    """

    def tokenize(self, text: str) -> Iterable[TokenSlice]:
        """Yield :class:`TokenSlice` objects for the supplied ``text``."""

        if not text:
            return []
        return (
            TokenSlice(match.group(0), match.end())
            for match in _TOKEN_PATTERN.finditer(text)
        )

    def count_tokens(self, text: str) -> int:
        """Return an estimated token count for ``text``."""

        if not text:
            return 0
        return len(_TOKEN_PATTERN.findall(text))

    def truncate(self, text: str, max_tokens: int) -> str:
        """Truncate ``text`` so that it does not exceed ``max_tokens`` tokens."""

        if not text or max_tokens <= 0:
            return ""

        count = 0
        cutoff = None
        for slice_ in self.tokenize(text):
            count += 1
            cutoff = slice_.end
            if count >= max_tokens:
                break

        # Nothing to truncate.
        total_tokens = self.count_tokens(text)
        if total_tokens <= max_tokens:
            return text.strip()

        truncated = text[: cutoff or 0].rstrip()
        if not truncated:
            return ""

        # Append ellipsis to indicate truncation while keeping spacing tidy.
        if not truncated.endswith("…"):
            truncated = f"{truncated} …"
        return truncated
