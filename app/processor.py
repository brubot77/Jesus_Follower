import re
from datetime import date

from app.briefings import format_daily_email
from app.config import Config
from app.db import (
    connect,
    upsert_user,
    remove_user,
    add_completion,
    get_users,
    get_reading_by_date,
    daily_email_already_sent,
    mark_daily_email_sent,
    is_active_user,
)
from app.gmail_client import GmailClient, GmailMessage
from app.parser import extract_completed_dates
from app.reports import build_user_report, build_group_status_report


def normalize_subject(message: GmailMessage) -> str:
    return (message.subject or "").strip().lower()


def is_admin(config: Config, message: GmailMessage) -> bool:
    return message.sender_email.lower().strip() == config.admin_email.lower().strip()


def is_bible_study_completion(message: GmailMessage) -> bool:
    return normalize_subject(message) == "bible study"


def is_bible_study_status_request(message: GmailMessage) -> bool:
    return normalize_subject(message) == "bible study status"


def is_add_user_request(message: GmailMessage) -> bool:
    return normalize_subject(message) == "bible study add user"


def is_remove_user_request(message: GmailMessage) -> bool:
    return normalize_subject(message) == "bible study remove user"


def extract_email_from_text(text: str) -> str | None:
    match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text or "", flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(0).lower().strip()


def extract_name_from_text(text: str) -> str | None:
    for line in (text or "").splitlines():
        line = line.strip()
        if line.lower().startswith("name:"):
            name = line.split(":", 1)[1].strip()
            return name or None
    return None


def reject_non_admin(config: Config, gmail: GmailClient, message: GmailMessage) -> None:
    gmail.send_email(
        to=message.sender_email,
        subject="Bible Study Admin Request Denied",
        body=(
            "This Bible Study admin request was denied.\n\n"
            f"Only {config.admin_email} is authorized to add or remove users."
        ),
        thread_id=message.thread_id,
    )
    gmail.add_label(message.message_id, config.failed_label)


def reject_non_user(config: Config, gmail: GmailClient, message: GmailMessage) -> None:
    gmail.send_email(
        to=message.sender_email,
        subject="Bible Study Request Denied",
        body=(
            "Your Bible Study email was received, but your email address is not currently "
            "an active approved user for this Bible Study.\n\n"
            "Ask the Bible Study admin to add you first."
        ),
        thread_id=message.thread_id,
    )
    gmail.add_label(message.message_id, config.failed_label)


def process_add_user_email(config: Config, gmail: GmailClient, message: GmailMessage) -> None:
    if not is_admin(config, message):
        reject_non_admin(config, gmail, message)
        return

    target_email = extract_email_from_text(message.body)
    target_name = extract_name_from_text(message.body)

    if not target_email:
        gmail.send_email(
            to=message.sender_email,
            subject="Bible Study Add User Failed",
            body=(
                "I could not find an email address to add.\n\n"
                "Use this format:\n"
                "Subject: Bible Study Add User\n\n"
                "newuser@example.com\n"
                "Name: John Smith"
            ),
            thread_id=message.thread_id,
        )
        gmail.add_label(message.message_id, config.failed_label)
        return

    with connect(config.database_path) as conn:
        upsert_user(
            conn=conn,
            email=target_email,
            display_name=target_name,
            signup_date=date.today().isoformat(),
        )
        conn.commit()

    gmail.send_email(
        to=message.sender_email,
        subject="Bible Study User Added",
        body=(
            "User added or reactivated.\n\n"
            f"Email: {target_email}\n"
            f"Name: {target_name or ''}\n"
            f"Signup date: {date.today().isoformat()}"
        ),
        thread_id=message.thread_id,
    )

    gmail.add_label(message.message_id, config.processed_label)


def process_remove_user_email(config: Config, gmail: GmailClient, message: GmailMessage) -> None:
    if not is_admin(config, message):
        reject_non_admin(config, gmail, message)
        return

    target_email = extract_email_from_text(message.body)

    if not target_email:
        gmail.send_email(
            to=message.sender_email,
            subject="Bible Study Remove User Failed",
            body=(
                "I could not find an email address to remove.\n\n"
                "Use this format:\n"
                "Subject: Bible Study Remove User\n\n"
                "newuser@example.com"
            ),
            thread_id=message.thread_id,
        )
        gmail.add_label(message.message_id, config.failed_label)
        return

    with connect(config.database_path) as conn:
        remove_user(conn=conn, email=target_email)
        conn.commit()

    gmail.send_email(
        to=message.sender_email,
        subject="Bible Study User Removed",
        body=(
            "User removed from active Bible Study emails.\n\n"
            f"Email: {target_email}"
        ),
        thread_id=message.thread_id,
    )

    gmail.add_label(message.message_id, config.processed_label)


def process_completion_email(config: Config, gmail: GmailClient, message: GmailMessage) -> None:
    with connect(config.database_path) as conn:
        if not is_active_user(conn, message.sender_email):
            reject_non_user(config, gmail, message)
            return

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
        if not is_active_user(conn, message.sender_email) and not is_admin(config, message):
            reject_non_user(config, gmail, message)
            return

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
            if is_add_user_request(message):
                process_add_user_email(config, gmail, message)
                processed_count += 1
            elif is_remove_user_request(message):
                process_remove_user_email(config, gmail, message)
                processed_count += 1
            elif is_bible_study_completion(message):
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