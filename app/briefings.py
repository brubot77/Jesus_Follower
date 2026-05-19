PASSAGE_BRIEFINGS = {
    "Genesis 1-3": {
        "overview": (
            "Genesis 1-3 introduces the beginning of creation, humanity, sin, judgment, "
            "and the first promise of redemption. God creates the heavens and the earth, "
            "forms mankind in His image, places Adam and Eve in the garden, and gives them "
            "a command. Their disobedience brings sin, shame, curse, and separation, but God "
            "also gives the first hope that the offspring of the woman will crush the serpent."
        ),
        "context": (
            "This passage sets the foundation for the entire Bible. It explains who God is "
            "as Creator, who humans are as image-bearers, why the world is broken, and why "
            "mankind needs rescue. Genesis 3:15 is often understood as the first gospel promise, "
            "pointing forward to Christ’s victory over sin and Satan."
        ),
        "cross_references": [
            "John 1:1-3",
            "Romans 5:12-19",
            "1 Corinthians 15:21-22",
            "Colossians 1:15-17",
            "Revelation 21:1-5",
        ],
        "key_takeaways": [
            "God is the sovereign Creator of all things.",
            "Human beings are made in the image of God and have unique dignity and responsibility.",
            "Sin begins with doubting God’s word and goodness.",
            "The fall explains why shame, death, conflict, and separation exist.",
            "God responds to sin with judgment, but also with mercy and a promise of redemption.",
        ],
        "application": (
            "Where are you tempted to doubt God’s word or goodness? What would it look like "
            "today to trust Him as Creator, Lord, and Redeemer?"
        ),
    },
    "Genesis 4-7": {
        "overview": (
            "Genesis 4-7 shows the spread of sin after the fall. Cain murders Abel, human "
            "violence and corruption increase, and the world becomes filled with wickedness. "
            "Yet Noah finds favor with God. God commands Noah to build the ark, preserving "
            "Noah’s family and the animals through judgment."
        ),
        "context": (
            "This section shows that sin is not isolated to Adam and Eve. It spreads through "
            "humanity and corrupts society. The flood is both an act of judgment and an act of "
            "preservation. Noah’s ark points forward to salvation through faith and God’s provision "
            "of rescue from judgment."
        ),
        "cross_references": [
            "Hebrews 11:4",
            "Hebrews 11:7",
            "Matthew 24:37-39",
            "1 Peter 3:20-21",
            "2 Peter 2:5",
        ],
        "key_takeaways": [
            "Sin grows when anger, jealousy, and pride are left unchecked.",
            "God sees both outward actions and inward motives.",
            "Human wickedness grieves God and brings judgment.",
            "Noah demonstrates faith through obedient action.",
            "God provides a way of rescue even when judgment is deserved.",
        ],
        "application": (
            "Is there anger, jealousy, or compromise that needs to be brought before God today? "
            "Where is God calling you to obey even if others do not understand?"
        ),
    },
    "Genesis 8-11": {
        "overview": (
            "Genesis 8-11 describes the end of the flood, God’s covenant with Noah, the renewed "
            "command to fill the earth, and humanity’s rebellion at Babel. God preserves life, "
            "sets the rainbow as a covenant sign, and later scatters the nations when mankind "
            "tries to make a name for itself apart from Him."
        ),
        "context": (
            "After the flood, the world receives a new beginning, but human sin remains. The tower "
            "of Babel shows that even after judgment and mercy, people still seek self-exaltation. "
            "This prepares the way for Genesis 12, where God begins His redemptive plan through "
            "Abram and promises blessing to all nations."
        ),
        "cross_references": [
            "Genesis 12:1-3",
            "Acts 2:1-12",
            "Romans 1:21-25",
            "Revelation 7:9-10",
        ],
        "key_takeaways": [
            "God remembers His people and keeps His promises.",
            "The rainbow points to God’s covenant mercy after judgment.",
            "A fresh start does not remove mankind’s need for a changed heart.",
            "Babel reveals the danger of pride and self-glory.",
            "God’s plan is bigger than one people or one nation.",
        ],
        "application": (
            "Are you trying to build your own name, security, or identity apart from God? "
            "What would it look like to seek His glory over your own?"
        ),
    },
    "Genesis 12-15": {
        "overview": (
            "Genesis 12-15 begins the story of Abram. God calls Abram to leave his country and "
            "promises to make him a great nation, bless him, and bless all families of the earth "
            "through him. Abram obeys, struggles, worships, rescues Lot, and believes God’s promise. "
            "Genesis 15 says Abram believed the Lord, and it was counted to him as righteousness."
        ),
        "context": (
            "This is a major turning point in the Bible. After humanity’s rebellion at Babel, God "
            "begins His covenant plan through Abram. The promise to bless all nations ultimately "
            "points forward to Jesus Christ, the offspring of Abraham, through whom salvation comes "
            "to the world."
        ),
        "cross_references": [
            "Romans 4:1-5",
            "Galatians 3:6-9",
            "Galatians 3:16",
            "Hebrews 11:8-12",
            "James 2:23",
        ],
        "key_takeaways": [
            "God’s call often requires trust before all details are visible.",
            "Abram’s righteousness came by faith, not by earning it.",
            "God’s promises move forward even through imperfect people.",
            "The blessing promised to Abram points ultimately to Christ.",
            "Faith responds to God’s word with trust and obedience.",
        ],
        "application": (
            "Where is God asking you to trust His promise before you see the full outcome? "
            "What step of obedience is in front of you today?"
        ),
    },
}


def build_daily_briefing(reference: str) -> dict:
    """
    Returns a passage-specific devotional/study briefing when available.

    This intentionally does not include full copyrighted Bible text.
    User should read the passage from their own Bible, preferably NLV.
    """

    normalized_reference = (reference or "").strip()

    if normalized_reference in PASSAGE_BRIEFINGS:
        return PASSAGE_BRIEFINGS[normalized_reference]

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