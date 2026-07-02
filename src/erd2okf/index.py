"""index.md: der OKF-Einstiegspunkt eines Schema-Ordners.

Progressive Disclosure für Agenten (ein File lesen, alles verlinkt finden),
Tabellen-Liste für Menschen, Mermaid-ERD als rekonstruierbares Diagramm.
Anders als die Tabellen-Files hat die index.md keinen handgepflegten Anteil:
sie gehört vollständig `generate`, Semantik gehört in die Tabellen-Bodies.
"""

import yaml

from erd2okf.introspect import Table
from erd2okf.okf import OKF_VERSION

INDEX_TYPE = "database-schema"

_OWNERSHIP_NOTE = (
    "<!-- Von erd2okf generiert. Hand-Edits gehen bei der nächsten Generierung\n"
    "     verloren — Semantik gehört in den Body der Tabellen-Files. -->"
)


def _erd(tables: list[Table]) -> str:
    known = {t.name for t in tables}
    lines = ["erDiagram"]
    for table in tables:
        lines.append(f"    {table.name} {{")
        for col in table.columns:
            keys = [k for k, set_ in (("PK", col.primary_key), ("FK", col.references)) if set_]
            suffix = f" {', '.join(keys)}" if keys else ""
            lines.append(f"        {col.type} {col.name}{suffix}")
        lines.append("    }")
    for table in tables:
        pk_cols = [c for c in table.columns if c.primary_key]
        for col in table.columns:
            if not col.references:
                continue
            parent = col.references.split(".")[0]
            if parent not in known:
                continue
            # 1:1 nur, wenn die FK-Spalte der ganze PK ist (Sub-Typ-Tabellen);
            # als Teil eines Verbund-PK (Brückentabellen) bleibt es n:1
            one_to_one = col.primary_key and len(pk_cols) == 1
            cardinality = "|o--||" if one_to_one else "}o--||"
            lines.append(f'    {table.name} {cardinality} {parent} : "{col.name}"')
    return "\n".join(lines)


def _one_line(text: str) -> str:
    return " ".join(text.split()).replace("|", "\\|")


def render_index(tables: list[Table], title: str) -> str:
    count = f"{len(tables)} Tabelle{'n' if len(tables) != 1 else ''}"
    front = yaml.safe_dump(
        {
            "type": INDEX_TYPE,
            "title": title,
            "description": f"Generierter OKF-Snapshot eines Datenbankschemas: {count}.",
            "okf": OKF_VERSION,
        },
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )

    rows = "\n".join(
        f"| [{t.name}](./{t.name}.md) | {_one_line(t.comment) if t.comment else ''} |"
        for t in tables
    )
    return (
        f"---\n{front}---\n\n"
        f"{_OWNERSHIP_NOTE}\n\n"
        f"# {title}\n\n"
        f"| Tabelle | Beschreibung |\n| --- | --- |\n{rows}\n\n"
        f"## ERD\n\n"
        f"```mermaid\n{_erd(tables)}\n```\n"
    )
