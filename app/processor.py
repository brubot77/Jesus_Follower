from datetime import date

from app.briefings import format_daily_email
from app.config import Config
from app.db import (
    connect,
    upsert_user,
    add_completion,
    get_users,
    get_reading_by_date,
    daily_email_already_sent,
    mark_daily_email_sent,
)
from app.gmail_client import GmailClient, GmailMessage
from app.parser import extract_completed_dates
from app.reports import build_user_report, build_group_status_report


def is_bible_study_completion(message: GmailMessage) -> bool:
    subject = (message.subject or "").strip().lower()
    return subject == "bible study"


def is_bible_study_status_request(message: GmailMessage) -> bool:
    subject = (message.subject or "").strip().lower()
    return subject == "bible study status"


def process_completion_email(config: Config, gmail: GmailClient, message: GmailMessage) -> None:
    default_year = date.today().year
    dates = extract_completed_dates(message.body, default_year=default_year)

    if not dates:
        gmail.send_email(
            to=message.sender_email,
            subject="Bible Study - No dates found",
            body=(
                "I received your Bible Study email, but I could not find any completed dates.\n\n"
                "Please reply using a format like:\n"
                "Completed May 19, 2026\n"
                "or\n"
                "Completed May 19, 2026 through May 21, 2026"
            ),
            thread_id=message.thread_id,
        )
        gmail.add_label(message.message_id, config.failed_label)
        return

    with connect(config.database_path) as conn:
        upsert_user(
            conn=conn,
            email=message.sender_email,
            display_name=message.sender_name,
            signup_date=date.today().isoformat(),
        )

        for reading_date in dates:
            add_completion(
                conn=conn,
                user_email=message.sender_email,
                reading_date=reading_date,
                source_message_id=message.message_id,
            )

        conn.commit()

        report = build_user_report(
            conn=conn,
            email=message.sender_email,
        )

    gmail.send_email(
        to=message.sender_email,
        subject="Bible Study Progress Updated",
        body=(
            f"Recorded {len(dates)} completed reading date(s):\n"
            + "\n".join([f"- {d}" for d in dates])
            + "\n\n"
            + report
        ),
        thread_id=message.thread_id,
    )

    gmail.add_label(message.message_id, config.processed_label)


def process_status_email(config: Config, gmail: GmailClient, message: GmailMessage) -> None:
    with connect(config.database_path) as conn:
        report = build_group_status_report(conn=conn)

    gmail.send_email(
        to=message.sender_email,
        subject="Bible Study Group Status",
        body=report,
        thread_id=message.thread_id,
    )

    gmail.add_label(message.message_id, config.processed_label)


def process_inbox(config: Config, max_results: int = 10) -> int:
    gmail = GmailClient(
        credentials_path=config.gmail_credentials_path,
        token_path=config.gmail_token_path,
    )

    message_ids = gmail.search_message_ids(
        query=config.gmail_query,
        max_results=max_results,
    )

    processed_count = 0

    for message_id in message_ids:
        message = gmail.get_message(message_id)

        try:
            if is_bible_study_completion(message):
                process_completion_email(config, gmail, message)
                processed_count += 1
            elif is_bible_study_status_request(message):
                process_status_email(config, gmail, message)
                processed_count += 1
        except Exception:
            gmail.add_label(message.message_id, config.failed_label)
            raise

    return processed_count


def send_daily_readings(config: Config, reading_date: str | None = None, force: bool = False) -> int:
    if reading_date is None:
        reading_date = date.today().isoformat()

    gmail = GmailClient(
        credentials_path=config.gmail_credentials_path,
        token_path=config.gmail_token_path,
    )

    sent_count = 0

    with connect(config.database_path) as conn:
        reading = get_reading_by_date(conn, reading_date)

        if not reading:
            print(f"No reading found for {reading_date}.")
            return 0

        users = get_users(conn)

        for user in users:
            email = user["email"]

            if not force and daily_email_already_sent(conn, email, reading_date):
                continue

            subject, body = format_daily_email(
                reading_date=reading["reading_date"],
                plan_day=reading["plan_day"],
                reference=reading["reference"],
            )

            gmail.send_email(
                to=email,
                subject=subject,
                body=body,
            )

            mark_daily_email_sent(conn, email, reading_date)
            conn.commit()

            sent_count += 1

    return sent_count