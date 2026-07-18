import re
import unicodedata


LEGAL_PREFIXES = {
    "SC",
}

LEGAL_SUFFIXES = {
    "SRL",
    "SA",
    "PFA",
    "SNC",
    "SCS",
    "SCA",
    "II",
    "IF",
    "CMI",
}


class InvalidTaxIdError(ValueError):
    pass


class InvalidCompanyNameError(ValueError):
    pass


def remove_diacritics(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)

    return "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )


def normalize_tax_id(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip().upper()
    normalized = re.sub(r"[\s.\-]", "", normalized)

    if not normalized:
        return None

    if normalized.startswith("RO"):
        normalized = normalized[2:]

    if not normalized.isdigit():
        raise InvalidTaxIdError(
            "CUI-ul trebuie să conțină doar cifre, opțional precedate de RO."
        )

    if len(normalized) > 20:
        raise InvalidTaxIdError("CUI-ul introdus este prea lung.")

    return normalized


def input_contains_vat_prefix(value: str | None) -> bool:
    if not value:
        return False

    normalized = re.sub(r"[\s.\-]", "", value.strip().upper())
    return normalized.startswith("RO")


def normalize_company_name(value: str) -> str:
    normalized = remove_diacritics(value).upper()
    normalized = re.sub(r"[^A-Z0-9]+", " ", normalized)
    tokens = normalized.split()

    while tokens and tokens[0] in LEGAL_PREFIXES:
        tokens.pop(0)

    while tokens and tokens[-1] in LEGAL_SUFFIXES:
        tokens.pop()

    if not tokens:
        raise InvalidCompanyNameError(
            "Denumirea companiei nu conține un nume valid."
        )

    return " ".join(tokens)