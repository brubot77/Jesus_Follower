from datetime import date
from tabulate import tabulate

from app.db import get_users, get_readings, get_user_completions


def _today_iso() -> str:
    return date.today().isoformat()


def get_next_open_reading(conn, email: str):
    readings = get_readings(conn)
    completed = get_user_completions(conn, email)

    for r in readings:
        if r["reading_date"] not in completed:
            return r

    return None


def build_user_report(conn, email: str, today_iso: str | None = None) -> str:
    if today_iso is None:
        today_iso = _today_iso()

    readings = get_readings(conn)
    completed = get_user_completions(conn, email)

    due_readings = [r for r in readings if r["reading_date"] <= today_iso]
    total_due = len(due_readings)
    total_completed = len([r for r in due_readings if r["reading_date"] in completed])

    percent = 0
    if total_due:
        percent = round((total_completed / total_due) * 100, 1)

    recent_rows = []
    for r in due_readings[-21:]:
        status = "Complete" if r["reading_date"] in completed else "Open"
        recent_rows.append(
            [
                r["reading_date"],
                r["plan_day"],
                r["reference"],
                status,
            ]
        )

    report = []
    report.append(f"Bible Study Progress Report for {email}")
    report.append("")
    report.append(f"Completed: {total_completed} of {total_due} due readings")
    report.append(f"Progress: {percent}%")
    report.append("")
    report.append("Recent Reading Status")
    report.append(
        tabulate(
            recent_rows,
            headers=["Date", "Day", "Reading", "Status"],
            tablefmt="github",
        )
    )

    next_open = get_next_open_reading(conn, email)

    if next_open:
        report.append("")
        report.append("Next open reading:")
        report.append(f"{next_open['reading_date']} — Day {next_open['plan_day']} — {next_open['reference']}")

    return "\n".join(report)


def build_group_status_report(conn, today_iso: str | None = None) -> str:
    if today_iso is None:
        today_iso = _today_iso()

    users = get_users(conn)
    readings = get_readings(conn)
    due_readings = [r for r in readings if r["reading_date"] <= today_iso]
    total_due = len(due_readings)

    rows = []

    for user in users:
        email = user["email"]
        completed = get_user_completions(conn, email)

        completed_due = len([r for r in due_readings if r["reading_date"] in completed])
        percent = 0
        if total_due:
            percent = round((completed_due / total_due) * 100, 1)

        next_open = get_next_open_reading(conn, email)

        rows.append(
            [
                email,
                user["signup_date"],
                completed_due,
                total_due,
                f"{percent}%",
                next_open["reading_date"] if next_open else "Done",
                next_open["reference"] if next_open else "Done",
            ]
        )

    report = []
    report.append("Bible Study Group Status")
    report.append("")
    report.append(
        tabulate(
            rows,
            headers=[
                "User",
                "Signup Date",
                "Completed",
                "Due",
                "Progress",
                "Next Open Date",
                "Next Reading",
            ],
            tablefmt="github",
        )
    )

    return "\n".join(report)