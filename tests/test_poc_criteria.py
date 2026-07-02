"""Die Erfolgskriterien des PoC aus PRODUCT_VISION.md, wörtlich, gegen data/test-model.sql.

Der PoC ist gescheitert, wenn ein gelöschtes Feld grün durchläuft
oder die Semantik bei einer Regeneration verloren geht.
"""

from pathlib import Path

import pytest
import yaml

from erd2okf.cli import main
from erd2okf.okf import parse

TEST_MODEL = Path(__file__).parent.parent / "data" / "test-model.sql"

ALL_TABLES = {
    "companies", "users", "roles", "user_roles",
    "vehicle_fleets", "vehicles", "truck_details", "drone_details",
    "vehicle_telemetry",
    "shipments", "route_plans", "route_stops",
}


@pytest.fixture
def model_db(db):
    db.execute(TEST_MODEL.read_text())
    return db


def test_every_table_becomes_a_file(model_db, pg_dsn, tmp_path):
    """Namens-Set DB gleich Namens-Set Files, plus die index.md der OKF-Spec.

    Vertragserweiterung vom 2026-07-02, von Thorsten autorisiert: OKF sieht
    eine index.md pro Verzeichnis vor (progressive Disclosure).
    """
    main(["generate", "--dsn", pg_dsn, "--out", str(tmp_path)])

    assert {p.stem for p in tmp_path.glob("*.md")} == ALL_TABLES | {"index"}


def test_index_is_okf_conformant_and_links_every_table(model_db, pg_dsn, tmp_path):
    """Vertragserweiterung vom 2026-07-02: die index.md ist der Einstiegspunkt.

    Sie trägt das Pflichtfeld der Spec und verlinkt jede Tabelle als
    Markdown-Link — daraus ist das ERD rekonstruierbar.
    """
    main(["generate", "--dsn", pg_dsn, "--out", str(tmp_path)])

    text = (tmp_path / "index.md").read_text()
    front = yaml.safe_load(text.split("---\n")[1])
    assert front["type"]
    for table in ALL_TABLES:
        assert f"](./{table}.md)" in text


def test_fresh_generate_is_green(model_db, pg_dsn, tmp_path):
    main(["generate", "--dsn", pg_dsn, "--out", str(tmp_path)])

    assert main(["check", "--dsn", pg_dsn, "--dir", str(tmp_path)]) == 0


@pytest.mark.parametrize(
    "mutation",
    [
        "CREATE TABLE invoices (id UUID PRIMARY KEY)",                # Tabelle add
        "DROP TABLE drone_details",                                   # Tabelle drop
        "ALTER TABLE truck_details RENAME TO lorry_details",          # Tabelle rename
        "ALTER TABLE vehicles ADD COLUMN color VARCHAR(20)",          # Spalte add
        "ALTER TABLE vehicles DROP COLUMN status",                    # Spalte drop
        "ALTER TABLE vehicles RENAME COLUMN vin TO chassis_number",   # Spalte rename
        "ALTER TABLE shipments ALTER COLUMN weight_kg TYPE VARCHAR(20)",  # Typ-Klasse
    ],
)
def test_structural_drift_turns_red(model_db, pg_dsn, tmp_path, mutation):
    """add, drop und rename von Tabellen und Spalten färben rot."""
    main(["generate", "--dsn", pg_dsn, "--out", str(tmp_path)])

    model_db.execute(mutation)

    assert main(["check", "--dsn", pg_dsn, "--dir", str(tmp_path)]) == 1


@pytest.mark.parametrize(
    "mutation",
    [
        "ALTER TABLE companies ALTER COLUMN name TYPE VARCHAR(500)",      # Länge
        "ALTER TABLE vehicles ALTER COLUMN license_plate TYPE TEXT",      # varchar->text
        "ALTER TABLE shipments ALTER COLUMN weight_kg TYPE NUMERIC(12,4)",  # Präzision
        "ALTER TABLE users ALTER COLUMN is_active SET NOT NULL",          # Nullability
    ],
)
def test_below_type_class_stays_green(model_db, pg_dsn, tmp_path, mutation):
    """Bewusst nichts unterhalb der Typ-Klasse prüfen."""
    main(["generate", "--dsn", pg_dsn, "--out", str(tmp_path)])

    model_db.execute(mutation)

    assert main(["check", "--dsn", pg_dsn, "--dir", str(tmp_path)]) == 0


def test_semantics_survive_regeneration(model_db, pg_dsn, tmp_path):
    """Handgepflegter Freitext übersteht eine Regeneration nach Schema-Änderung."""
    main(["generate", "--dsn", pg_dsn, "--out", str(tmp_path)])
    users_file = tmp_path / "users.md"
    semantics = (
        "Mitarbeiter der jeweiligen Mandanten.\n\n"
        "## Gelernt im Betrieb\n\n"
        "Soft-Delete läuft über is_active, nie über DELETE."
    )
    front, sep, _old_body = users_file.read_text().rpartition("---\n")
    users_file.write_text(front + sep + "\n" + semantics + "\n")

    model_db.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMPTZ")
    main(["generate", "--dsn", pg_dsn, "--out", str(tmp_path)])

    table, body = parse(users_file.read_text())
    assert body == semantics
    assert "last_login" in [c.name for c in table.columns]


def test_db_comments_land_in_the_files(model_db, pg_dsn, tmp_path):
    """Vertragsänderung vom 2026-07-02, von Thorsten beauftragt: der Tabellen-Comment
    lebt nur im description-Feld, der Body startet leer — keine Dopplung.
    """
    main(["generate", "--dsn", pg_dsn, "--out", str(tmp_path)])

    table, body = parse((tmp_path / "companies.md").read_text())
    assert table.comment == (
        "Zentrale Mandantentabelle. "
        "Jedes Asset und jeder User muss einer Company zugeordnet sein."
    )
    assert body == ""
    settings = next(c for c in table.columns if c.name == "settings")
    assert settings.comment and "Feature-Flags" in settings.comment
