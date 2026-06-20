"""
Delta Lake explorer — loads all local Delta tables into DuckDB views
and drops into an interactive SQL shell.

Usage:
    python explore_delta.py            # interactive shell
    python explore_delta.py --list     # list available tables
    python explore_delta.py --query "SELECT * FROM ttt_plays LIMIT 10"
"""

import argparse
import os
import sys
from pathlib import Path

import duckdb

DELTA_ROOT = Path(__file__).parent / "data" / "delta"


def _discover_tables(root: Path) -> dict[str, Path]:
    """Walk two levels deep: domain/table_name."""
    tables = {}
    for domain_dir in sorted(root.iterdir()):
        if not domain_dir.is_dir():
            continue
        for table_dir in sorted(domain_dir.iterdir()):
            if not table_dir.is_dir() or table_dir.name.startswith("_"):
                continue
            if (table_dir / "_delta_log").exists():
                view_name = f"{domain_dir.name}_{table_dir.name}"
                tables[view_name] = table_dir
    return tables


def _register_views(conn: duckdb.DuckDBPyConnection, tables: dict[str, Path]) -> None:
    conn.execute("INSTALL delta; LOAD delta;")
    for view_name, path in tables.items():
        conn.execute(
            f"CREATE OR REPLACE VIEW {view_name} AS "
            f"SELECT * FROM delta_scan('{path.as_posix()}');"
        )


def _print_table_list(tables: dict[str, Path]) -> None:
    print("\nAvailable views:\n")
    for name, path in tables.items():
        print(f"  {name:<40}  {path.relative_to(DELTA_ROOT.parent.parent)}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Explore Delta Lake tables via DuckDB")
    parser.add_argument(
        "--list", action="store_true", help="List available tables and exit"
    )
    parser.add_argument(
        "--query", "-q", metavar="SQL", help="Run a single SQL query and exit"
    )
    args = parser.parse_args()

    tables = _discover_tables(DELTA_ROOT)
    if not tables:
        print(f"No Delta tables found under {DELTA_ROOT}")
        sys.exit(1)

    conn = duckdb.connect()
    _register_views(conn, tables)

    if args.list:
        _print_table_list(tables)
        return

    if args.query:
        result = conn.execute(args.query).fetchdf()
        print(result.to_string(index=False))
        return

    # Interactive shell
    _print_table_list(tables)
    print("Type SQL queries, '.tables' to list views, or 'exit' to quit.\n")

    while True:
        try:
            sql = input("duckdb> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not sql:
            continue
        if sql.lower() in ("exit", "quit", r"\q"):
            break
        if sql.lower() in (".tables", r"\dt"):
            _print_table_list(tables)
            continue

        try:
            result = conn.execute(sql).fetchdf()
            print(result.to_string(index=False))
            print(f"\n({len(result)} rows)\n")
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
