"""Abbildung von Postgres-Datentypen auf Typ-Klassen.

Drift wird auf dieser Ebene geprüft: Wechsel innerhalb einer Klasse
(varchar(10) -> varchar(20), timestamp mit/ohne Zeitzone) sind egal,
Wechsel der Klasse (varchar -> integer) sind Drift.
"""

_TYPE_CLASSES = {
    "character varying": "text",
    "character": "text",
    "text": "text",
    "integer": "integer",
    "bigint": "integer",
    "smallint": "integer",
    "numeric": "numeric",
    "real": "float",
    "double precision": "float",
    "timestamp with time zone": "timestamp",
    "timestamp without time zone": "timestamp",
    "date": "date",
    "time with time zone": "time",
    "time without time zone": "time",
    "boolean": "boolean",
    "uuid": "uuid",
    "jsonb": "json",
    "json": "json",
    "bytea": "bytea",
    "ARRAY": "array",
}


def type_class(pg_type: str) -> str:
    """Liefert die Typ-Klasse eines Postgres-Typs; Unbekanntes unverändert."""
    return _TYPE_CLASSES.get(pg_type, pg_type)
