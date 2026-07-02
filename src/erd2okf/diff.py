"""Vergleicht DB-Struktur gegen die OKF-Files — auf Typ-Klassen-Ebene.

Grün heißt: keine strukturell relevante Drift (Tabellen- und Spalten-Sets
identisch, Typ-Klassen identisch). Nicht: Schema identisch.
"""

from dataclasses import dataclass

from erd2okf.introspect import Table

_MESSAGES = {
    "table_added": "Tabelle {table} existiert in der DB, aber nicht in den Files",
    "table_removed": "Tabelle {table} existiert in den Files, aber nicht in der DB",
    "column_added": "Spalte {table}.{column} existiert in der DB, aber nicht in den Files",
    "column_removed": "Spalte {table}.{column} existiert in den Files, aber nicht in der DB",
    "type_changed": "Spalte {table}.{column}: Typ-Klasse {detail}",
}


@dataclass(frozen=True)
class Drift:
    kind: str
    table: str
    column: str | None = None
    detail: str | None = None

    def __str__(self) -> str:
        return _MESSAGES[self.kind].format(
            table=self.table, column=self.column, detail=self.detail
        )


def diff(db_tables: list[Table], doc_tables: list[Table]) -> list[Drift]:
    """Drift zwischen Live-DB (Ist) und OKF-Files (dokumentiert)."""
    db = {t.name: t for t in db_tables}
    doc = {t.name: t for t in doc_tables}
    findings: list[Drift] = []

    for name in sorted(db.keys() - doc.keys()):
        findings.append(Drift("table_added", name))
    for name in sorted(doc.keys() - db.keys()):
        findings.append(Drift("table_removed", name))

    for name in sorted(db.keys() & doc.keys()):
        db_cols = {c.name: c for c in db[name].columns}
        doc_cols = {c.name: c for c in doc[name].columns}
        for col in sorted(db_cols.keys() - doc_cols.keys()):
            findings.append(Drift("column_added", name, col))
        for col in sorted(doc_cols.keys() - db_cols.keys()):
            findings.append(Drift("column_removed", name, col))
        for col in sorted(db_cols.keys() & doc_cols.keys()):
            actual, documented = db_cols[col].type, doc_cols[col].type
            if actual != documented:
                findings.append(
                    Drift(
                        "type_changed",
                        name,
                        col,
                        f"dokumentiert als {documented}, in der DB {actual}",
                    )
                )
    return findings
