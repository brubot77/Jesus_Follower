import sqlite3
from pathlib import Path
from datetime import datetime


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    display_name TEXT,
    signup_date TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_day INTEGER NOT NULL UNIQUE,
    reading_date TEXT NOT NULL,
    reference TEXT NOT NULL,
    title TEXT,
    overview TEXT,
    cross_references TEXT,
    key_takeaways TEXT
);

CREATE TABLE IF NOT EXISTS user_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    reading_date TEXT NOT NULL,
    completed_utc TEXT NOT NULL,
    source_message_id TEXT,
    UNIQUE(user_email, reading_date)
);

CREATE TABLE IF NOT EXISTS inbound_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gmail_message_id TEXT NOT NULL UNIQUE,
    sender_email TEXT NOT NULL,
    subject TEXT,
    body TEXT,
    processed_utc TEXT,
    status TEXT,
    error TEXT
);

CREATE TABLE IF NOT EXISTS daily_emails_sent (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    reading_date TEXT NOT NULL,
    sent_utc TEXT NOT NULL,
    UNIQUE(user_email, reading_date)
);
"""


def connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


def upsert_user(conn: sqlite3.Connection, email: str, display_name: str | None, signup_date: str) -> None:
    conn.execute(
        """
        INSERT INTO users (email, display_name, signup_date, active, created_utc)
        VALUES (?, ?, ?, 1, ?)
        ON CONFLICT(email) DO UPDATE SET
            display_name = COALESCE(excluded.display_name, users.display_name),
            signup_date = COALESCE(users.signup_date, excluded.signup_date),
            active = 1
        """,
        (email.lower().strip(), display_name, signup_date, datetime.utcnow().isoformat()),
    )


def remove_user(conn: sqlite3.Connection, email: str) -> None:
    conn.execute(
        """
        UPDATE users
        SET active = 0
        WHERE email = ?
        """,
        (email.lower().strip(),),
    )


def add_completion(
    conn: sqlite3.Connection,
    user_email: str,
    reading_date: str,
    source_message_id: str | None = None,
) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO user_completions
        (user_email, reading_date, completed_utc, source_message_id)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_email.lower().strip(),
            reading_date,
            datetime.utcnow().isoformat(),
            source_message_id,
        ),
    )


def get_users(conn: sqlite3.Connection):
    return conn.execute(
        """
        SELECT email, display_name, signup_date, active
        FROM users
        WHERE active = 1
        ORDER BY email
        """
    ).fetchall()


def get_readings(conn: sqlite3.Connection):
    return conn.execute(
        """
        SELECT *
        FROM readings
        ORDER BY reading_date
        """
    ).fetchall()


def get_reading_by_date(conn: sqlite3.Connection, reading_date: str):
    return conn.execute(
        """
        SELECT *
        FROM readings
        WHERE reading_date = ?
        LIMIT 1
        """,
        (reading_date,),
    ).fetchone()


def get_user_completions(conn: sqlite3.Connection, email: str):
    rows = conn.execute(
        """
        SELECT reading_date
        FROM user_completions
        WHERE user_email = ?
        ORDER BY reading_date
        """,
        (email.lower().strip(),),
    ).fetchall()

    return {r["reading_date"] for r in rows}


def daily_email_already_sent(conn: sqlite3.Connection, user_email: str, reading_date: str) -> bool:
    row = conn.execute(
        """
        SELECT id
        FROM daily_emails_sent
        WHERE user_email = ?
          AND reading_date = ?
        LIMIT 1
        """,
        (user_email.lower().strip(), reading_date),
    ).fetchone()

    return row is not None


def mark_daily_email_sent(conn: sqlite3.Connection, user_email: str, reading_date: str) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO daily_emails_sent
        (user_email, reading_date, sent_utc)
        VALUES (?, ?, ?)
        """,
        (
            user_email.lower().strip(),
            reading_date,
            datetime.utcnow().isoformat(),
        ),
    )