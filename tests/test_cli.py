"""CLI: `erd2okf generate` schreibt die Files, `erd2okf check` ist der CI-Backstop."""

from erd2okf.cli import main


def test_generate_writes_okf_files(db, pg_dsn, tmp_path):
    db.execute("CREATE TABLE companies (id UUID PRIMARY KEY, name TEXT NOT NULL)")

    exit_code = main(["generate", "--dsn", pg_dsn, "--out", str(tmp_path)])

    assert exit_code == 0
    assert (tmp_path / "companies.md").exists()


def test_check_is_green_after_generate(db, pg_dsn, tmp_path, capsys):
    db.execute("CREATE TABLE companies (id UUID PRIMARY KEY)")
    main(["generate", "--dsn", pg_dsn, "--out", str(tmp_path)])

    exit_code = main(["check", "--dsn", pg_dsn, "--dir", str(tmp_path)])

    assert exit_code == 0
    assert "keine strukturell relevante drift" in capsys.readouterr().out.lower()


def test_check_is_red_after_column_drop(db, pg_dsn, tmp_path, capsys):
    db.execute("CREATE TABLE companies (id UUID PRIMARY KEY, vat VARCHAR(50))")
    main(["generate", "--dsn", pg_dsn, "--out", str(tmp_path)])
    db.execute("ALTER TABLE companies DROP COLUMN vat")

    exit_code = main(["check", "--dsn", pg_dsn, "--dir", str(tmp_path)])

    assert exit_code == 1
    assert "companies.vat" in capsys.readouterr().out


def test_check_is_green_for_change_below_type_class(db, pg_dsn, tmp_path):
    db.execute("CREATE TABLE companies (id UUID PRIMARY KEY, vat VARCHAR(10))")
    main(["generate", "--dsn", pg_dsn, "--out", str(tmp_path)])
    db.execute("ALTER TABLE companies ALTER COLUMN vat TYPE VARCHAR(20)")

    exit_code = main(["check", "--dsn", pg_dsn, "--dir", str(tmp_path)])

    assert exit_code == 0


def test_exclude_flag_extends_the_default_exclude_list(db, pg_dsn, tmp_path):
    db.execute("CREATE TABLE companies (id UUID PRIMARY KEY)")
    db.execute("CREATE TABLE scratch (id UUID PRIMARY KEY)")
    db.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) PRIMARY KEY)")

    main(["generate", "--dsn", pg_dsn, "--out", str(tmp_path), "--exclude", "scratch"])

    assert {p.name for p in tmp_path.glob("*.md")} == {"companies.md", "index.md"}


def test_check_fails_loudly_when_dir_missing(pg_dsn, tmp_path, capsys):
    exit_code = main(["check", "--dsn", pg_dsn, "--dir", str(tmp_path / "nope")])

    assert exit_code == 2
    assert "nope" in capsys.readouterr().err
