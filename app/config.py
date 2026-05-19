import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Config:
    gmail_credentials_path: str
    gmail_token_path: str

    database_path: str
    plan_path: str
    briefings_path: str
    log_file: str

    study_start_date: str
    bot_email: str

    gmail_query: str
    processed_label: str
    failed_label: str

    weekly_report_day: str


def get_config() -> Config:
    return Config(
        gmail_credentials_path=os.getenv("GMAIL_CREDENTIALS_PATH", ""),
        gmail_token_path=os.getenv("GMAIL_TOKEN_PATH", ""),

        database_path=os.getenv("DATABASE_PATH", "./data/jesus_follower.sqlite3"),
        plan_path=os.getenv("PLAN_PATH", "./data/bible_plan.json"),
        briefings_path=os.getenv("BRIEFINGS_PATH", "./data/briefings.json"),
        log_file=os.getenv("LOG_FILE", "./logs/jesus_follower.log"),

        study_start_date=os.getenv("STUDY_START_DATE", "2026-05-19"),
        bot_email=os.getenv("BOT_EMAIL", "bru.bot77@gmail.com"),

        gmail_query=os.getenv(
            "GMAIL_QUERY",
            "in:inbox -label:JesusFollower/Processed -label:JesusFollower/Failed",
        ),
        processed_label=os.getenv("PROCESSED_LABEL", "JesusFollower/Processed"),
        failed_label=os.getenv("FAILED_LABEL", "JesusFollower/Failed"),

        weekly_report_day=os.getenv("WEEKLY_REPORT_DAY", "MONDAY"),
    )