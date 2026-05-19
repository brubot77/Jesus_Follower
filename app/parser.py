import re
from datetime import date, timedelta
from dateutil import parser as date_parser


MONTH_PATTERN = (
    r"January|February|March|April|May|June|July|August|September|October|November|December|"
    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
)


def normalize_date(value: str, default_year: int | None = None) -> str:
    value = value.strip()

    if default_year is None:
        default_year = date.today().year

    # If text is like "May 19" with no year, add default year.
    if not re.search(r"\b\d{4}\b", value):
        value = f"{value}, {default_year}"

    parsed = date_parser.parse(value, fuzzy=True)
    return parsed.date().isoformat()


def expand_date_range(start_iso: str, end_iso: str) -> list[str]:
    start = date.fromisoformat(start_iso)
    end = date.fromisoformat(end_iso)

    if end < start:
        start, end = end, start

    days = []
    current = start
    while current <= end:
        days.append(current.isoformat())
        current += timedelta(days=1)

    return days


def extract_completed_dates(text: str, default_year: int | None = None) -> list[str]:
    """
    Extracts dates from email/plain text.

    Supports examples:
      May 19, 2026
      May 19 2026
      2026-05-19
      5/19/2026
      May 19, 2026 through May 22, 2026
      May 19, 2026 - May 22, 2026
    """
    if not text:
        return []

    if default_year is None:
        default_year = date.today().year

    found_dates: set[str] = set()

    # ISO dates: 2026-05-19
    for match in re.findall(r"\b\d{4}-\d{1,2}-\d{1,2}\b", text):
        try:
            found_dates.add(normalize_date(match, default_year))
        except Exception:
            pass

    # Slash dates: 5/19/2026 or 05/19/26
    for match in re.findall(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", text):
        try:
            found_dates.add(normalize_date(match, default_year))
        except Exception:
            pass

    # Month name dates: May 19, 2026 or May 19
    month_date_pattern = rf"\b(?:{MONTH_PATTERN})\.?\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?\b"
    month_matches = re.findall(month_date_pattern, text, flags=re.IGNORECASE)

    cleaned_month_matches = []
    for match in month_matches:
        cleaned = re.sub(r"(st|nd|rd|th)\b", "", match, flags=re.IGNORECASE)
        cleaned_month_matches.append(cleaned)

        try:
            found_dates.add(normalize_date(cleaned, default_year))
        except Exception:
            pass

    # Date ranges with "through", "to", or hyphen.
    range_pattern = (
        rf"((?:{MONTH_PATTERN})\.?\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?|\d{{4}}-\d{{1,2}}-\d{{1,2}}|\d{{1,2}}/\d{{1,2}}/\d{{2,4}})"
        rf"\s*(?:through|thru|to|-)\s*"
        rf"((?:{MONTH_PATTERN})\.?\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?|\d{{4}}-\d{{1,2}}-\d{{1,2}}|\d{{1,2}}/\d{{1,2}}/\d{{2,4}})"
    )

    for start_raw, _, end_raw, _ in re.findall(range_pattern, text, flags=re.IGNORECASE):
        try:
            start_clean = re.sub(r"(st|nd|rd|th)\b", "", start_raw, flags=re.IGNORECASE)
            end_clean = re.sub(r"(st|nd|rd|th)\b", "", end_raw, flags=re.IGNORECASE)

            start_iso = normalize_date(start_clean, default_year)
            end_iso = normalize_date(end_clean, default_year)

            for expanded in expand_date_range(start_iso, end_iso):
                found_dates.add(expanded)
        except Exception:
            pass

    return sorted(found_dates)