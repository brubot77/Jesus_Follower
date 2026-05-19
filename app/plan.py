import json
from datetime import date, timedelta
from pathlib import Path
from app.db import connect


READING_PLAN_REFERENCES = [
    "Genesis 1-3", "Genesis 4-7", "Genesis 8-11", "Genesis 12-15", "Genesis 16-18",
    "Genesis 19-21", "Genesis 22-24", "Genesis 25-27", "Genesis 28-30", "Genesis 31-33",
    "Genesis 34-36", "Genesis 37-39", "Genesis 40-42", "Genesis 43-46", "Genesis 47-50",

    "Exodus 1-4", "Exodus 5-7", "Exodus 8-10", "Exodus 11-13", "Exodus 14-16",
    "Exodus 17-20", "Exodus 21-24", "Exodus 25-27", "Exodus 28-31", "Exodus 32-34",
    "Exodus 35-37", "Exodus 38-40",

    "Leviticus 1-4", "Leviticus 5-7", "Leviticus 8-10", "Leviticus 11-13",
    "Leviticus 14-15", "Leviticus 16-18", "Leviticus 19-21", "Leviticus 22-24",
    "Leviticus 25-27",

    "Numbers 1-3", "Numbers 4-6", "Numbers 7-9", "Numbers 10-12", "Numbers 13-15",
    "Numbers 16-18", "Numbers 19-21", "Numbers 22-24", "Numbers 25-27", "Numbers 28-30",
    "Numbers 31-33", "Numbers 34-36",

    "Deuteronomy 1-3", "Deuteronomy 4-6", "Deuteronomy 7-9", "Deuteronomy 10-12",
    "Deuteronomy 13-16", "Deuteronomy 17-20", "Deuteronomy 21-23", "Deuteronomy 24-27",
    "Deuteronomy 28-30", "Deuteronomy 31-34",

    "Joshua 1-4", "Joshua 5-8", "Joshua 9-12", "Joshua 13-16", "Joshua 17-20",
    "Joshua 21-24",

    "Judges 1-3", "Judges 4-6", "Judges 7-9", "Judges 10-12", "Judges 13-15",
    "Judges 16-18", "Judges 19-21",

    "Ruth 1-4",

    "1 Samuel 1-3", "1 Samuel 4-7", "1 Samuel 8-10", "1 Samuel 11-13",
    "1 Samuel 14-16", "1 Samuel 17-20", "1 Samuel 21-24", "1 Samuel 25-27",
    "1 Samuel 28-31",

    "2 Samuel 1-3", "2 Samuel 4-7", "2 Samuel 8-11", "2 Samuel 12-14",
    "2 Samuel 15-18", "2 Samuel 19-21", "2 Samuel 22-24",

    "1 Kings 1-3", "1 Kings 4-7", "1 Kings 8-10", "1 Kings 11-13", "1 Kings 14-16",
    "1 Kings 17-19", "1 Kings 20-22",

    "2 Kings 1-3", "2 Kings 4-6", "2 Kings 7-9", "2 Kings 10-12", "2 Kings 13-15",
    "2 Kings 16-18", "2 Kings 19-21", "2 Kings 22-25",

    "1 Chronicles 1-4", "1 Chronicles 5-8", "1 Chronicles 9-12", "1 Chronicles 13-16",
    "1 Chronicles 17-20", "1 Chronicles 21-24", "1 Chronicles 25-29",

    "2 Chronicles 1-4", "2 Chronicles 5-8", "2 Chronicles 9-12", "2 Chronicles 13-16",
    "2 Chronicles 17-20", "2 Chronicles 21-24", "2 Chronicles 25-28",
    "2 Chronicles 29-32", "2 Chronicles 33-36",

    "Ezra 1-3", "Ezra 4-6", "Ezra 7-10",
    "Nehemiah 1-3", "Nehemiah 4-6", "Nehemiah 7-9", "Nehemiah 10-13",
    "Esther 1-5", "Esther 6-10",

    "Job 1-4", "Job 5-8", "Job 9-12", "Job 13-16", "Job 17-20", "Job 21-24",
    "Job 25-28", "Job 29-32", "Job 33-36", "Job 37-42",

    "Psalms 1-8", "Psalms 9-16", "Psalms 17-24", "Psalms 25-32", "Psalms 33-40",
    "Psalms 41-48", "Psalms 49-56", "Psalms 57-64", "Psalms 65-72", "Psalms 73-80",
    "Psalms 81-88", "Psalms 89-96", "Psalms 97-104", "Psalms 105-112",
    "Psalms 113-120", "Psalms 121-128", "Psalms 129-136", "Psalms 137-144",
    "Psalms 145-150",

    "Proverbs 1-4", "Proverbs 5-8", "Proverbs 9-12", "Proverbs 13-16",
    "Proverbs 17-20", "Proverbs 21-24", "Proverbs 25-28", "Proverbs 29-31",

    "Ecclesiastes 1-4", "Ecclesiastes 5-8", "Ecclesiastes 9-12",
    "Song of Solomon 1-8",

    "Isaiah 1-4", "Isaiah 5-8", "Isaiah 9-12", "Isaiah 13-16", "Isaiah 17-20",
    "Isaiah 21-24", "Isaiah 25-28", "Isaiah 29-32", "Isaiah 33-36", "Isaiah 37-39",
    "Isaiah 40-43", "Isaiah 44-47", "Isaiah 48-51", "Isaiah 52-55", "Isaiah 56-59",
    "Isaiah 60-63", "Isaiah 64-66",

    "Jeremiah 1-3", "Jeremiah 4-6", "Jeremiah 7-9", "Jeremiah 10-13",
    "Jeremiah 14-17", "Jeremiah 18-21", "Jeremiah 22-25", "Jeremiah 26-29",
    "Jeremiah 30-33", "Jeremiah 34-37", "Jeremiah 38-41", "Jeremiah 42-45",
    "Jeremiah 46-49", "Jeremiah 50-52",

    "Lamentations 1-5",

    "Ezekiel 1-4", "Ezekiel 5-8", "Ezekiel 9-12", "Ezekiel 13-16",
    "Ezekiel 17-20", "Ezekiel 21-24", "Ezekiel 25-28", "Ezekiel 29-32",
    "Ezekiel 33-36", "Ezekiel 37-40", "Ezekiel 41-44", "Ezekiel 45-48",

    "Daniel 1-3", "Daniel 4-6", "Daniel 7-9", "Daniel 10-12",

    "Hosea 1-4", "Hosea 5-9", "Hosea 10-14",
    "Joel 1-3", "Amos 1-4", "Amos 5-9",
    "Obadiah 1", "Jonah 1-4", "Micah 1-4", "Micah 5-7",
    "Nahum 1-3", "Habakkuk 1-3", "Zephaniah 1-3",
    "Haggai 1-2", "Zechariah 1-4", "Zechariah 5-8", "Zechariah 9-14",
    "Malachi 1-4",

    "Matthew 1-4", "Matthew 5-7", "Matthew 8-10", "Matthew 11-13",
    "Matthew 14-17", "Matthew 18-20", "Matthew 21-23", "Matthew 24-26",
    "Matthew 27-28",

    "Mark 1-3", "Mark 4-6", "Mark 7-9", "Mark 10-12", "Mark 13-16",

    "Luke 1-3", "Luke 4-6", "Luke 7-9", "Luke 10-12", "Luke 13-15",
    "Luke 16-18", "Luke 19-21", "Luke 22-24",

    "John 1-3", "John 4-6", "John 7-9", "John 10-12", "John 13-15",
    "John 16-18", "John 19-21",

    "Acts 1-3", "Acts 4-6", "Acts 7-9", "Acts 10-12", "Acts 13-15",
    "Acts 16-18", "Acts 19-21", "Acts 22-24", "Acts 25-28",

    "Romans 1-4", "Romans 5-8", "Romans 9-12", "Romans 13-16",

    "1 Corinthians 1-4", "1 Corinthians 5-8", "1 Corinthians 9-12",
    "1 Corinthians 13-16",

    "2 Corinthians 1-4", "2 Corinthians 5-9", "2 Corinthians 10-13",

    "Galatians 1-3", "Galatians 4-6",
    "Ephesians 1-3", "Ephesians 4-6",
    "Philippians 1-4", "Colossians 1-4",

    "1 Thessalonians 1-5", "2 Thessalonians 1-3",
    "1 Timothy 1-3", "1 Timothy 4-6",
    "2 Timothy 1-4",
    "Titus 1-3", "Philemon 1",

    "Hebrews 1-4", "Hebrews 5-8", "Hebrews 9-13",

    "James 1-5",
    "1 Peter 1-5",
    "2 Peter 1-3",
    "1 John 1-5",
    "2 John 1", "3 John 1", "Jude 1",

    "Revelation 1-3", "Revelation 4-7", "Revelation 8-11",
    "Revelation 12-15", "Revelation 16-19", "Revelation 20-22",
]


def generate_plan(start_date: str, output_path: str) -> list[dict]:
    start = date.fromisoformat(start_date)

    plan = []
    for index, reference in enumerate(READING_PLAN_REFERENCES, start=1):
        plan.append(
            {
                "plan_day": index,
                "reading_date": (start + timedelta(days=index - 1)).isoformat(),
                "reference": reference,
                "title": f"Day {index}: {reference}",
            }
        )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)

    return plan


def load_plan_to_db(db_path: str, plan_path: str) -> None:
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)

    with connect(db_path) as conn:
        for item in plan:
            conn.execute(
                """
                INSERT OR REPLACE INTO readings
                (plan_day, reading_date, reference, title, overview, cross_references, key_takeaways)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["plan_day"],
                    item["reading_date"],
                    item["reference"],
                    item.get("title"),
                    item.get("overview", ""),
                    item.get("cross_references", ""),
                    item.get("key_takeaways", ""),
                ),
            )

        conn.commit()