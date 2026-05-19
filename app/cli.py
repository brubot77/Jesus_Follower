import argparse
from datetime import date
from pathlib import Path

from app.config import get_config
from app.db import init_db, connect, upsert_user, add_completion
from app.parser import extract_completed_dates
from app.plan import generate_plan, load_plan_to_db
from app.reports import build_user_report, build_group_status_report


def cmd_init(args):
    config = get_config()

    Path(config.database_path).parent.mkdir(parents=True, exist_ok=True)
    Path(config.plan_path).parent.mkdir(parents=True, exist_ok=True)
    Path(config.briefings_path).parent.mkdir(parents=True, exist_ok=True)
    Path(config.log_file).parent.mkdir(parents=True, exist_ok=True)

    init_db(config.database_path)

    print("Jesus_Follower initialized.")
    print(f"Database: {config.database_path}")
    print(f"Plan path: {config.plan_path}")
    print(f"Log file: {config.log_file}")


def cmd_generate_plan(args):
    config = get_config()

    plan = generate_plan(
        start_date=config.study_start_date,
        output_path=config.plan_path,
    )

    load_plan_to_db(
        db_path=config.database_path,
        plan_path=config.plan_path,
    )

    print("Bible reading plan generated and loaded into database.")
    print(f"Start date: {config.study_start_date}")
    print(f"Total reading days generated: {len(plan)}")
    print(f"Plan path: {config.plan_path}")

    if len(plan) != 365:
        print("")
        print("WARNING:")
        print(f"The current plan contains {len(plan)} days, not 365.")
        print("The app will still run, but the reading plan should be refined to exactly 365 days.")


def cmd_status(args):
    config = get_config()

    with connect(config.database_path) as conn:
        user_count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        reading_count = conn.execute("SELECT COUNT(*) AS c FROM readings").fetchone()["c"]
        completion_count = conn.execute("SELECT COUNT(*) AS c FROM user_completions").fetchone()["c"]

    print("Jesus_Follower status")
    print("---------------------")
    print(f"Users: {user_count}")
    print(f"Readings: {reading_count}")
    print(f"Completions: {completion_count}")
    print(f"Database: {config.database_path}")


def cmd_add_user(args):
    config = get_config()

    signup_date = args.signup_date or date.today().isoformat()

    with connect(config.database_path) as conn:
        upsert_user(
            conn=conn,
            email=args.email,
            display_name=args.name,
            signup_date=signup_date,
        )
        conn.commit()

    print("User added or updated.")
    print(f"Email: {args.email}")
    print(f"Name: {args.name or ''}")
    print(f"Signup date: {signup_date}")


def cmd_complete(args):
    config = get_config()

    default_year = args.default_year or date.today().year
    dates = extract_completed_dates(args.dates, default_year=default_year)

    if not dates:
        print("No valid completion dates found.")
        return

    with connect(config.database_path) as conn:
        upsert_user(
            conn=conn,
            email=args.email,
            display_name=None,
            signup_date=date.today().isoformat(),
        )

        for reading_date in dates:
            add_completion(
                conn=conn,
                user_email=args.email,
                reading_date=reading_date,
                source_message_id=None,
            )

        conn.commit()

    print(f"Recorded {len(dates)} completed reading date(s) for {args.email}:")
    for d in dates:
        print(f"- {d}")


def cmd_report_user(args):
    config = get_config()

    with connect(config.database_path) as conn:
        report = build_user_report(
            conn=conn,
            email=args.email,
            today_iso=args.today,
        )

    print(report)


def cmd_report_all(args):
    config = get_config()

    with connect(config.database_path) as conn:
        report = build_group_status_report(
            conn=conn,
            today_iso=args.today,
        )

    print(report)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="Jesus_Follower",
        description="Bible study tracking and daily reading agent.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize folders and database.")
    init_parser.set_defaults(func=cmd_init)

    plan_parser = subparsers.add_parser("generate-plan", help="Generate and load Bible reading plan.")
    plan_parser.set_defaults(func=cmd_generate_plan)

    status_parser = subparsers.add_parser("status", help="Show current database status.")
    status_parser.set_defaults(func=cmd_status)

    add_user_parser = subparsers.add_parser("add-user", help="Add or update a Bible study user.")
    add_user_parser.add_argument("--email", required=True)
    add_user_parser.add_argument("--name", required=False)
    add_user_parser.add_argument("--signup-date", required=False, help="YYYY-MM-DD")
    add_user_parser.set_defaults(func=cmd_add_user)

    complete_parser = subparsers.add_parser("complete", help="Record completed reading dates for a user.")
    complete_parser.add_argument("--email", required=True)
    complete_parser.add_argument(
        "--dates",
        required=True,
        help='Examples: "May 19, 2026" or "May 19, 2026 through May 22, 2026"',
    )
    complete_parser.add_argument("--default-year", required=False, type=int)
    complete_parser.set_defaults(func=cmd_complete)

    report_user_parser = subparsers.add_parser("report-user", help="Show one user's progress report.")
    report_user_parser.add_argument("--email", required=True)
    report_user_parser.add_argument("--today", required=False, help="Optional report-as-of date YYYY-MM-DD")
    report_user_parser.set_defaults(func=cmd_report_user)

    report_all_parser = subparsers.add_parser("report-all", help="Show all-user group progress report.")
    report_all_parser.add_argument("--today", required=False, help="Optional report-as-of date YYYY-MM-DD")
    report_all_parser.set_defaults(func=cmd_report_all)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()