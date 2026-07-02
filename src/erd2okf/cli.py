"""CLI: `erd2okf generate` nach der Migration, `erd2okf check` als CI-Backstop."""

import argparse
import sys
from pathlib import Path

import psycopg

from erd2okf.diff import diff
from erd2okf.generate import generate
from erd2okf.introspect import DEFAULT_EXCLUDE, introspect
from erd2okf.okf import parse


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="erd2okf",
        description="Postgres-Schema als OKF-Markdown im Repo, mit Drift-Check.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="OKF-Files aus der Live-DB (neu) schreiben")
    gen.add_argument("--dsn", required=True, help="Postgres-DSN")
    gen.add_argument("--out", required=True, type=Path, help="Zielordner")
    gen.add_argument("--schema", default="public")

    check = sub.add_parser("check", help="Drift zwischen DB und OKF-Files prüfen")
    check.add_argument("--dsn", required=True, help="Postgres-DSN")
    check.add_argument("--dir", required=True, type=Path, help="OKF-Ordner")
    check.add_argument("--schema", default="public")

    for cmd in (gen, check):
        cmd.add_argument(
            "--exclude",
            action="append",
            default=[],
            metavar="TABLE",
            help=f"Tabelle zusätzlich ausschließen (Standard: {', '.join(sorted(DEFAULT_EXCLUDE))})",
        )

    return parser


def _load_documented(okf_dir: Path):
    tables = []
    for path in sorted(okf_dir.glob("*.md")):
        try:
            table, _ = parse(path.read_text())
        except (ValueError, KeyError):
            continue
        tables.append(table)
    return tables


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    exclude = DEFAULT_EXCLUDE | set(args.exclude)
    with psycopg.connect(args.dsn) as conn:
        db_tables = introspect(conn, schema=args.schema, exclude=exclude)
        dbname = conn.info.dbname

    if args.command == "generate":
        title = dbname if args.schema == "public" else f"{dbname}.{args.schema}"
        generate(db_tables, args.out, title=title)
        print(f"{len(db_tables)} Tabellen nach {args.out} geschrieben")
        return 0

    if not args.dir.is_dir():
        print(f"OKF-Ordner nicht gefunden: {args.dir}", file=sys.stderr)
        return 2

    findings = diff(db_tables, _load_documented(args.dir))
    if not findings:
        print(f"OK — keine strukturell relevante Drift ({len(db_tables)} Tabellen)")
        return 0

    print(f"DRIFT — {len(findings)} Befund(e):")
    for finding in findings:
        print(f"  - {finding}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
