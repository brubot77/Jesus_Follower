import json
from pathlib import Path


def load_briefings(briefings_path: str | None = None) -> dict:
    if briefings_path is None:
        briefings_path = str(Path("data") / "briefings.json")

    path = Path(briefings_path)

    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_briefings(briefings_path: str, briefings: dict) -> None:
    path = Path(briefings_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(briefings, f, indent=2, ensure_ascii=False)


def validate_briefing_payload(payload: dict) -> tuple[bool, str]:
    required_fields = [
        "reference",
        "overview",
        "context",
        "cross_references",
        "key_takeaways",
        "application",
    ]

    for field in required_fields:
        if field not in payload:
            return False, f"Missing required field: {field}"

    if not isinstance(payload["reference"], str) or not payload["reference"].strip():
        return False, "reference must be a non-empty string"

    if not isinstance(payload["overview"], str) or not payload["overview"].strip():
        return False, "overview must be a non-empty string"

    if not isinstance(payload["context"], str) or not payload["context"].strip():
        return False, "context must be a non-empty string"

    if not isinstance(payload["cross_references"], list):
        return False, "cross_references must be a list"

    if not isinstance(payload["key_takeaways"], list):
        return False, "key_takeaways must be a list"

    if not isinstance(payload["application"], str) or not payload["application"].strip():
        return False, "application must be a non-empty string"

    return True, "OK"


def add_or_update_briefing(briefings_path: str, payload: dict) -> str:
    is_valid, message = validate_briefing_payload(payload)
    if not is_valid:
        raise ValueError(message)

    reference = payload["reference"].strip()

    entry = {
        "overview": payload["overview"].strip(),
        "context": payload["context"].strip(),
        "cross_references": [str(x).strip() for x in payload["cross_references"] if str(x).strip()],
        "key_takeaways": [str(x).strip() for x in payload["key_takeaways"] if str(x).strip()],
        "application": payload["application"].strip(),
    }

    briefings = load_briefings(briefings_path)
    briefings[reference] = entry
    save_briefings(briefings_path, briefings)

    return reference


def parse_briefing_json_from_text(text: str) -> dict:
    cleaned = (text or "").strip()

    # Allows email bodies that wrap JSON in ```json ... ```
    if "```" in cleaned:
        parts = cleaned.split("```")
        for part in parts:
            candidate = part.strip()
            if candidate.lower().startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{") and candidate.endswith("}"):
                return json.loads(candidate)

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in email body.")

    return json.loads(cleaned[start : end + 1])


def build_daily_briefing(reference: str, briefings_path: str | None = None) -> dict:
    normalized_reference = (reference or "").strip()
    briefings = load_briefings(briefings_path)

    if normalized_reference in briefings:
        briefing = briefings[normalized_reference]
        briefing["_approved"] = True
        return briefing

    return {
        "_approved": False,
        "overview": (
            "No approved briefing is currently available for this reading yet. "
            "Please read the passage directly in your own Bible, preferably NLV."
        ),
        "context": (
            "No approved context notes are currently available for this passage."
        ),
        "cross_references": [],
        "key_takeaways": [
            "Read the passage carefully and note what it reveals about God.",
            "Look for commands to obey, promises to trust, sins to avoid, and examples to follow.",
            "Ask how this passage fits into the larger story of Scripture and points to the need for Christ.",
        ],
        "application": (
            "What is one truth from this reading that should affect how you think, pray, speak, or act today?"
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
    ]

    if not briefing.get("_approved"):
        body_lines.extend(
            [
                "Briefing Status:",
                "No approved briefing is currently available for this reading yet.",
                "The notes below are limited so you can still continue the reading plan.",
                "",
            ]
        )

    body_lines.extend(
        [
            "Overview:",
            briefing.get("overview", ""),
            "",
            "Context:",
            briefing.get("context", ""),
            "",
            "Cross References:",
        ]
    )

    cross_references = briefing.get("cross_references", [])
    if cross_references:
        for item in cross_references:
            body_lines.append(f"- {item}")
    else:
        body_lines.append("- No approved cross references available yet.")

    body_lines.extend(["", "Key Takeaways:"])

    key_takeaways = briefing.get("key_takeaways", [])
    if key_takeaways:
        for item in key_takeaways:
            body_lines.append(f"- {item}")
    else:
        body_lines.append("- No approved key takeaways available yet.")

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
    briefing = build_daily_briefing(reference, briefings_path=briefings_path)

    if briefing.get("_approved"):
        subject = f"Bible Study - {reading_date} - {reference}"
    else:
        subject = f"Bible Study - {reading_date} - {reference} - Briefing Pending"

    body = format_reading_breakdown(
        reading_date=reading_date,
        plan_day=plan_day,
        reference=reference,
        briefings_path=briefings_path,
    )

    return subject, body