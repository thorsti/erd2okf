"""index.md: OKF-Einstiegspunkt pro Verzeichnis.

Verlinkt jede Tabelle (progressive Disclosure für Agenten) und trägt ein
Mermaid-ERD — damit ist das Diagramm aus den Files rekonstruierbar.
Anders als die Tabellen-Bodies gehört die index.md vollständig `generate`.
"""

import yaml

from erd2okf.generate import generate
from erd2okf.introspect import Column, Table


def _table(name, comment=None, columns=None):
    return Table(
        name=name,
        comment=comment,
        columns=columns
        or [Column(name="id", type="uuid", nullable=False, primary_key=True)],
    )


def _fk(name, references, primary_key=False):
    return Column(
        name=name, type="uuid", nullable=False,
        primary_key=primary_key, references=references,
    )


def test_index_frontmatter_is_okf_conformant(tmp_path):
    generate([_table("companies")], tmp_path, title="fleetdb")

    front = yaml.safe_load((tmp_path / "index.md").read_text().split("---\n")[1])

    assert front["type"] == "database-schema"
    assert front["title"] == "fleetdb"
    assert "1 Tabelle" in front["description"]


def test_index_links_every_table_with_its_description(tmp_path):
    generate(
        [
            _table("companies", comment="Zentrale Mandantentabelle."),
            _table("users"),
        ],
        tmp_path,
    )

    text = (tmp_path / "index.md").read_text()

    assert "[companies](./companies.md)" in text
    assert "[users](./users.md)" in text
    assert "Zentrale Mandantentabelle." in text


def test_index_erd_shows_foreign_keys_as_relationships(tmp_path):
    users = _table(
        "users",
        columns=[
            Column(name="id", type="uuid", nullable=False, primary_key=True),
            _fk("company_id", "companies.id"),
        ],
    )

    generate([_table("companies"), users], tmp_path)

    text = (tmp_path / "index.md").read_text()
    assert "```mermaid" in text
    assert 'users }o--|| companies : "company_id"' in text


def test_index_erd_marks_one_to_one_when_fk_is_the_pk(tmp_path):
    details = Table(
        name="truck_details",
        columns=[_fk("vehicle_id", "vehicles.id", primary_key=True)],
    )

    generate([_table("vehicles"), details], tmp_path)

    assert 'truck_details |o--|| vehicles : "vehicle_id"' in (
        tmp_path / "index.md"
    ).read_text()


def test_index_erd_composite_pk_bridge_table_is_not_one_to_one(tmp_path):
    """FK als Teil eines Verbund-PK (Brückentabelle) ist n:1, kein 1:1."""
    bridge = Table(
        name="user_roles",
        columns=[
            _fk("user_id", "users.id", primary_key=True),
            _fk("role_id", "roles.id", primary_key=True),
        ],
    )

    generate([_table("users"), _table("roles"), bridge], tmp_path)

    text = (tmp_path / "index.md").read_text()
    assert 'user_roles }o--|| users : "user_id"' in text
    assert 'user_roles }o--|| roles : "role_id"' in text


def test_index_erd_lists_columns_as_entity_attributes(tmp_path):
    generate(
        [
            _table(
                "companies",
                columns=[
                    Column(name="id", type="uuid", nullable=False, primary_key=True),
                    Column(name="name", type="text", nullable=False),
                ],
            )
        ],
        tmp_path,
    )

    text = (tmp_path / "index.md").read_text()
    assert "uuid id PK" in text
    assert "text name" in text


def test_index_is_fully_regenerated_not_merged(tmp_path):
    """Die index.md gehört generate — Semantik gehört in die Tabellen-Files."""
    generate([_table("companies")], tmp_path)
    index = tmp_path / "index.md"
    index.write_text(index.read_text() + "\nHandnotiz, die hier nicht hingehört.\n")

    generate([_table("companies")], tmp_path)

    assert "Handnotiz" not in index.read_text()


def test_dropped_table_disappears_from_index(tmp_path):
    generate([_table("companies"), _table("legacy")], tmp_path)

    generate([_table("companies")], tmp_path)

    assert "legacy" not in (tmp_path / "index.md").read_text()
