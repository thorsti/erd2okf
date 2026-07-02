"""OKF-Markdown: eine Datei pro Tabelle.

Struktur (maschinenlesbar) im YAML-Frontmatter, Semantik (Freitext) im Body.
Beim ersten Rendern wird der Body aus dem Tabellen-Comment der DB gesät.

OKF v0.1 verlangt pro Concept genau ein Pflichtfeld: `type`. `title` und
`description` sind reservierte Felder der Spec; `okf` und `table`/`columns`
sind erlaubte Custom-Felder.
"""

import yaml

from erd2okf.introspect import Column, Table

OKF_VERSION = 1
CONCEPT_TYPE = "database-table"


def render(table: Table, body: str | None = None) -> str:
    """Rendert eine Tabelle als OKF-Markdown."""
    columns = []
    for col in table.columns:
        entry: dict = {"name": col.name, "type": col.type, "nullable": col.nullable}
        if col.primary_key:
            entry["primary_key"] = True
        if col.references:
            entry["references"] = col.references
        if col.comment:
            entry["description"] = col.comment
        columns.append(entry)

    concept: dict = {"type": CONCEPT_TYPE, "title": table.name}
    if table.comment:
        concept["description"] = table.comment
    concept |= {"okf": OKF_VERSION, "table": table.name, "columns": columns}
    front = yaml.safe_dump(
        concept,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    if body is None:
        body = table.comment or ""
    return f"---\n{front}---\n\n{body.strip()}\n"


def parse(text: str) -> tuple[Table, str]:
    """Liest OKF-Markdown zurück in (Tabelle, Freitext-Body)."""
    if not text.startswith("---\n"):
        raise ValueError("Kein OKF-File: YAML-frontmatter fehlt")
    front_text, _, body = text[4:].partition("\n---\n")
    if not _:
        raise ValueError("Kein OKF-File: YAML-frontmatter nicht geschlossen")
    front = yaml.safe_load(front_text)

    body = body.strip()
    columns = [
        Column(
            name=entry["name"],
            type=entry["type"],
            nullable=entry["nullable"],
            primary_key=entry.get("primary_key", False),
            references=entry.get("references"),
            comment=entry.get("description"),
        )
        for entry in front.get("columns", [])
    ]
    table = Table(
        name=front["table"], columns=columns, comment=front.get("description")
    )
    return table, body
