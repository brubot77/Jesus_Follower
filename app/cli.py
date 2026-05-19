import argparse
from pathlib import Path

from app.config import get_config
from app.db import init_db, connect
from app.plan import generate_plan, load_plan_to_db


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

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()