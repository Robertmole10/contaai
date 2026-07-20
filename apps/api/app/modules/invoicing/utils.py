from __future__ import annotations

import re


def normalize_name_key(name: str) -> str:
    """
    Normalize a business partner name for duplicate detection.

    Example:
        " SC   ABC  SRL "
        ->
        "sc abc srl"
    """

    normalized = re.sub(r"\s+", " ", name.strip())

    return normalized.casefold()