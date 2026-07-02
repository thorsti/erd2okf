"""generate: schreibt den OKF-Ordner und hält ihn synchron zur DB-Struktur.

Die harte Zusage: Regeneration macht die handgepflegte Semantik nie platt.
"""

from erd2okf.generate import generate
from erd2okf.introspect import Column, Table
from erd2okf.okf import parse


def _table(name, comment=None, cols=("id",)):
    return Table(
        name=name,
        comment=comment,
        columns=[Column(name=c, type="uuid", nullable=False) for c in cols],
    )


def test_writes_one_file_per_table(tmp_path):
    generate([_table("companies"), _table("users")], tmp_path)

    assert sorted(p.name for p in tmp_path.glob("*.md")) == [
        "companies.md",
        "index.md",
        "users.md",
    ]


def test_seeds_body_from_table_comment_on_first_run(tmp_path):
    generate([_table("companies", comment="Zentrale Mandantentabelle.")], tmp_path)

    _, body = parse((tmp_path / "companies.md").read_text())
    assert body == "Zentrale Mandantentabelle."


def test_regeneration_preserves_hand_edited_body(tmp_path):
    generate([_table("users", comment="Aus der DB.")], tmp_path)
    okf_file = tmp_path / "users.md"
    front, sep, _body = okf_file.read_text().rpartition("---\n")
    okf_file.write_text(front + sep + "\nHandgepflegt: users.email ist der Login.\n")

    # Struktur ändert sich (neue Spalte), Semantik muss stehen bleiben
    generate([_table("users", comment="Aus der DB.", cols=("id", "email"))], tmp_path)

    table, body = parse(okf_file.read_text())
    assert body == "Handgepflegt: users.email ist der Login."
    assert [c.name for c in table.columns] == ["id", "email"]


def test_removes_files_for_dropped_tables(tmp_path):
    generate([_table("companies"), _table("legacy_stuff")], tmp_path)

    generate([_table("companies")], tmp_path)

    assert sorted(p.name for p in tmp_path.glob("*.md")) == [
        "companies.md",
        "index.md",
    ]


def test_warns_before_removing_file_with_hand_written_body(tmp_path, capsys):
    """Kein stiller Semantik-Verlust: das unlink eines gefüllten Bodys wird benannt."""
    generate([_table("legacy", comment="Handgepflegtes Wissen.")], tmp_path)

    generate([_table("other")], tmp_path)

    err = capsys.readouterr().err
    assert "legacy.md" in err and "git" in err


def test_removing_file_with_empty_body_is_silent(tmp_path, capsys):
    generate([_table("legacy")], tmp_path)

    generate([_table("other")], tmp_path)

    assert capsys.readouterr().err == ""


def test_leaves_non_okf_files_alone(tmp_path):
    (tmp_path / "README.md").write_text("# Über diesen Ordner\n")

    generate([_table("companies")], tmp_path)

    assert (tmp_path / "README.md").read_text() == "# Über diesen Ordner\n"


def test_creates_output_directory_if_missing(tmp_path):
    out = tmp_path / "docs" / "schema"

    generate([_table("companies")], out)

    assert (out / "companies.md").exists()
