import json
from pathlib import Path


def load_briefings(briefings_path: str | None = None) -> dict:
    """
    Loads passage-specific briefings from data/briefings.json.

    If the file is missing or invalid, returns an empty dictionary.
    """

    if briefings_path is None:
        briefings_path = str(Path("data") / "briefings.json")

    path = Path(briefings_path)

    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            return data

        return {}
    except Exception:
        return {}


def build_daily_briefing(reference: str, briefings_path: str | None = None) -> dict:
    """
    Returns a passage-specific devotional/study briefing when available.

    This intentionally does not include full copyrighted Bible text.
    User should read the passage from their own Bible, preferably NLV.
    """

    normalized_reference = (reference or "").strip()
    briefings = load_briefings(briefings_path)

    if normalized_reference in briefings:
        return briefings[normalized_reference]

    return {
        "overview": (
            f"Today’s reading is {reference}. Read the full passage in your own Bible, "
            "preferably NLV. As you read, identify the main events, commands, promises, "
            "warnings, examples of faith, examples of sin, and what the passage reveals about God."
        ),
        "context": (
            "This passage should be read as part of the larger storyline of Scripture: creation, "
            "fall, covenant, redemption, Christ, and restoration. Ask how this reading connects "
            "to what came before and how it points toward mankind’s need for God’s rescue."
        ),
        "cross_references": [
            "Luke 24:27",
            "John 5:39",
            "Romans 15:4",
            "2 Timothy 3:16-17",
        ],
        "key_takeaways": [
            "Look for what the passage reveals about God’s character.",
            "Look for what the passage reveals about human nature and sin.",
            "Identify commands to obey, promises to trust, and warnings to heed.",
            "Ask how this passage fits into God’s larger plan of redemption through Jesus Christ.",
        ],
        "application": (
            "What is one specific truth from today’s reading that should change how you think, "
            "pray, speak, or act today?"
        ),
    }


def format_reading_breakdown(
    reading_date: str,
    plan_day: int,
    reference: str,
    briefings_path: str | None = None,
) -> str:
    briefing = build_daily_briefing(reference, briefings_path=briefings_path)

    body_lines = [
        f"Bible Study - Day {plan_day}",
        "",
        f"Date: {reading_date}",
        f"Reading: {reference}",
        "",
        "Read this passage in your own Bible, preferably NLV.",
        "",
        "Overview:",
        briefing.get("overview", ""),
        "",
        "Context:",
        briefing.get("context", ""),
        "",
        "Cross References:",
    ]

    for item in briefing.get("cross_references", []):
        body_lines.append(f"- {item}")

    body_lines.extend(["", "Key Takeaways:"])

    for item in briefing.get("key_takeaways", []):
        body_lines.append(f"- {item}")

    body_lines.extend(
        [
            "",
            "Application:",
            briefing.get("application", ""),
            "",
            "To mark this reading complete, reply with:",
            f"Completed {reading_date}",
            "",
            "You can also complete multiple days like:",
            "Completed May 19, 2026 through May 21, 2026",
        ]
    )

    return "\n".join(body_lines)


def format_daily_email(
    reading_date: str,
    plan_day: int,
    reference: str,
    briefings_path: str | None = None,
) -> tuple[str, str]:
    subject = f"Bible Study - {reading_date} - {reference}"

    body = format_reading_breakdown(
        reading_date=reading_date,
        plan_day=plan_day,
        reference=reference,
        briefings_path=briefings_path,
    )

    return subject, body