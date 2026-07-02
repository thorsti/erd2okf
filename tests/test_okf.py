"""OKF-Format: Struktur im YAML-Frontmatter, Semantik im Freitext-Body."""

import pytest
import yaml

from erd2okf.introspect import Column, Table
from erd2okf.okf import parse, render


def _vehicles() -> Table:
    return Table(
        name="vehicles",
        comment="Stammdaten für Fahrzeuge aller Art.",
        columns=[
            Column(name="id", type="uuid", nullable=False, primary_key=True),
            Column(
                name="fleet_id",
                type="uuid",
                nullable=False,
                references="vehicle_fleets.id",
            ),
            Column(
                name="vin",
                type="text",
                nullable=False,
                comment="17-stellige Fahrgestellnummer.",
            ),
        ],
    )


def test_frontmatter_is_okf_spec_conformant():
    """OKF v0.1: genau ein Pflichtfeld pro Concept — type. title/description sind reserviert."""
    front = yaml.safe_load(render(_vehicles()).split("---\n")[1])

    assert front["type"] == "database-table"
    assert front["title"] == "vehicles"
    assert front["description"] == "Stammdaten für Fahrzeuge aller Art."


def test_description_is_omitted_without_table_comment():
    table = Table(
        name="route_plans",
        columns=[Column(name="id", type="uuid", nullable=False, primary_key=True)],
    )

    front = yaml.safe_load(render(table).split("---\n")[1])

    assert front["type"] == "database-table"
    assert "description" not in front


def test_references_carry_a_relative_file_path():
    """Design-Entscheidung vom 2026-07-02 (Thorsten): FK-Referenzen zeigen
    zusätzlich als relativer File-Pfad auf das OKF-File der Zieltabelle.
    """
    front = yaml.safe_load(render(_vehicles()).split("---\n")[1])

    by_name = {c["name"]: c for c in front["columns"]}
    assert by_name["fleet_id"]["references"] == "vehicle_fleets.id"
    assert by_name["fleet_id"]["references_file"] == "./vehicle_fleets.md"
    assert "references_file" not in by_name["vin"]


def test_render_produces_frontmatter_and_empty_body():
    text = render(_vehicles())

    assert text.startswith("---\n")
    front, body = text.split("---\n", 2)[1:]
    assert "table: vehicles" in front
    # Der Tabellen-Comment lebt nur im description-Feld — keine Dopplung im Body
    assert "Stammdaten für Fahrzeuge aller Art." in front
    assert body.strip() == ""


def test_render_parse_roundtrip_preserves_structure():
    original = _vehicles()

    table, body = parse(render(original))

    assert table == original
    assert body == ""


def test_render_with_explicit_body_keeps_that_body():
    text = render(_vehicles(), body="Handgepflegte Semantik.\n\nMit Absätzen.")

    _, body = parse(text)

    assert body.strip() == "Handgepflegte Semantik.\n\nMit Absätzen."


def test_render_without_comment_leaves_empty_body():
    table = Table(
        name="route_plans",
        columns=[Column(name="id", type="uuid", nullable=False, primary_key=True)],
    )

    parsed, body = parse(render(table))

    assert parsed == table
    assert body.strip() == ""


def test_parse_rejects_files_without_frontmatter():
    with pytest.raises(ValueError, match="frontmatter"):
        parse("# nur markdown, kein OKF\n")
