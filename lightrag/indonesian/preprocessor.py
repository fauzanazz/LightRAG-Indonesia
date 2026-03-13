"""Indonesian text preprocessor for LightRAG.

Performs lightweight preprocessing steps before text is fed to LightRAG.insert():
  1. Acronym expansion — appends full form in parentheses on first occurrence
  2. Text normalization — fixes common whitespace / encoding artifacts

Controlled by the USE_INDONESIAN_PREPROCESSING flag in addon_params.
When the flag is OFF, these functions are never called.
"""

from __future__ import annotations

import re
from typing import Optional

from lightrag.indonesian.acronyms import INDONESIAN_ACRONYMS


def expand_acronyms(
    text: str,
    acronym_map: Optional[dict[str, str]] = None,
) -> str:
    """Expand acronyms by appending the full form in parentheses on first occurrence.

    Example:
        "BPOM mengeluarkan izin" → "BPOM (Badan Pengawas Obat dan Makanan) mengeluarkan izin"

    Only the *first* occurrence of each acronym is expanded so the text stays
    readable. Subsequent occurrences are left as-is.

    Args:
        text: Raw input text.
        acronym_map: Custom mapping ``{acronym: full_form}``.
            Defaults to ``INDONESIAN_ACRONYMS``.

    Returns:
        Text with first-occurrence acronyms expanded.
    """
    if acronym_map is None:
        acronym_map = INDONESIAN_ACRONYMS

    seen: set[str] = set()

    def _replace_first(match: re.Match) -> str:
        token = match.group(0)
        # Try exact match first, then case-insensitive
        full = acronym_map.get(token)
        if full is None:
            # Try matching with different casing
            for key, value in acronym_map.items():
                if key.upper() == token.upper():
                    full = value
                    token = key  # normalize to canonical form
                    break
        if full is None:
            return match.group(0)
        if token in seen:
            return match.group(0)
        seen.add(token)
        return f"{match.group(0)} ({full})"

    # Build a regex that matches any acronym as a whole word.
    # Sort by length descending so longer acronyms match first.
    sorted_acronyms = sorted(acronym_map.keys(), key=len, reverse=True)
    pattern = r"\b(?:" + "|".join(re.escape(a) for a in sorted_acronyms) + r")\b"
    return re.sub(pattern, _replace_first, text)


def normalize_text(text: str) -> str:
    """Apply lightweight text normalization.

    Steps:
        - Collapse multiple whitespace (including nbsp) into a single space.
        - Strip leading/trailing whitespace per line.
        - Remove zero-width characters.
        - Normalize common Unicode dash/quote variants.

    Args:
        text: Raw input text.

    Returns:
        Normalized text.
    """
    # Remove zero-width characters
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)

    # Normalize Unicode dashes to ASCII hyphen-minus
    text = re.sub(r"[\u2013\u2014\u2015]", "-", text)

    # Normalize smart quotes to straight quotes
    text = re.sub(r"[\u201c\u201d]", '"', text)
    text = re.sub(r"[\u2018\u2019]", "'", text)

    # Collapse multiple whitespace (incl. non-breaking space) to single space
    text = re.sub(r"[ \t\u00a0]+", " ", text)

    # Strip each line
    text = "\n".join(line.strip() for line in text.splitlines())

    # Collapse 3+ consecutive newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def preprocess_indonesian_text(
    text: str,
    acronym_map: Optional[dict[str, str]] = None,
) -> str:
    """Full preprocessing pipeline for Indonesian text.

    Applies normalization first, then acronym expansion.
    This function is intended to be called before ``LightRAG.insert()``.

    Args:
        text: Raw evidence or article text.
        acronym_map: Optional custom acronym mapping.

    Returns:
        Preprocessed text ready for LightRAG ingestion.
    """
    text = normalize_text(text)
    text = expand_acronyms(text, acronym_map)
    return text
