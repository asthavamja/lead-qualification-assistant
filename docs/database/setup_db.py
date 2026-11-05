import sqlite3
from pathlib import Path


DATABASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = DATABASE_DIR / "technova_company.sqlite3"


def main():
    schema = (DATABASE_DIR / "schema.sql").read_text(encoding="utf-8")
    seed = (DATABASE_DIR / "seed.sql").read_text(encoding="utf-8")

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executescript(schema)
        connection.executescript(seed)

        services = connection.execute(
            "SELECT COUNT(*) FROM service_catalog"
        ).fetchone()[0]
        process_steps = connection.execute(
            "SELECT COUNT(*) FROM project_process_steps"
        ).fetchone()[0]
        policies = connection.execute(
            "SELECT COUNT(*) FROM company_policies"
        ).fetchone()[0]

    print(f"SQLite database ready: {DATABASE_PATH}")
    print(
        f"Loaded {services} services, {process_steps} process steps, "
        f"and {policies} policies."
    )


if __name__ == "__main__":
    main()
