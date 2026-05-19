def build_daily_briefing(reference: str) -> dict:
    """
    Creates a simple devotional/study briefing from the reading reference.

    This intentionally does not include full copyrighted Bible text.
    User should read the passage from their own Bible, preferably NLV.
    """

    return {
        "overview": (
            f"Today’s reading is {reference}. Read the full passage in your own Bible, "
            "preferably NLV. As you read, look for what the passage reveals about God, "
            "human nature, sin, faith, obedience, judgment, mercy, and redemption."
        ),
        "context": (
            "Pay attention to where this reading fits in the larger story of Scripture. "
            "Ask: What happened before this? What promise, command, warning, or act of God "
            "is being developed? How does this passage point toward the need for Christ?"
        ),
        "cross_references": [
            "Luke 24:27",
            "John 5:39",
            "Romans 15:4",
            "2 Timothy 3:16-17",
        ],
        "key_takeaways": [
            "God reveals His character through both His words and His actions.",
            "Scripture often shows both human failure and God’s faithfulness.",
            "Look for commands to obey, promises to trust, sins to avoid, and truths to believe.",
            "Ask how this passage fits into God’s larger plan of redemption through Jesus Christ.",
        ],
        "application": (
            "What is one specific truth from today’s reading that should change how you think, "
            "pray, speak, or act today?"
        ),
    }


def format_reading_breakdown(reading_date: str, plan_day: int, reference: str) -> str:
    briefing = build_daily_briefing(reference)

    body_lines = [
        f"Bible Study - Day {plan_day}",
        "",
        f"Date: {reading_date}",
        f"Reading: {reference}",
        "",
        "Read this passage in your own Bible, preferably NLV.",
        "",
        "Overview:",
        briefing["overview"],
        "",
        "Context:",
        briefing["context"],
        "",
        "Cross References:",
    ]

    for item in briefing["cross_references"]:
        body_lines.append(f"- {item}")

    body_lines.extend(["", "Key Takeaways:"])

    for item in briefing["key_takeaways"]:
        body_lines.append(f"- {item}")

    body_lines.extend(
        [
            "",
            "Application:",
            briefing["application"],
            "",
            "To mark this reading complete, reply with:",
            f"Completed {reading_date}",
            "",
            "You can also complete multiple days like:",
            "Completed May 19, 2026 through May 21, 2026",
        ]
    )

    return "\n".join(body_lines)


def format_daily_email(reading_date: str, plan_day: int, reference: str) -> tuple[str, str]:
    subject = f"Bible Study - {reading_date} - {reference}"
    body = format_reading_breakdown(
        reading_date=reading_date,
        plan_day=plan_day,
        reference=reference,
    )
    return subject, body