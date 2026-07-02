"""Typ-Klassen: die Ebene, auf der Drift geprüft wird.

varchar(10) -> varchar(20) ist egal, varchar -> integer nicht.
"""

import pytest

from erd2okf.typeclass import type_class


@pytest.mark.parametrize(
    ("pg_type", "expected"),
    [
        # Textliches: Länge ist unterhalb der Typ-Klasse
        ("character varying", "text"),
        ("character", "text"),
        ("text", "text"),
        # Ganzzahlen: Breite ist unterhalb der Typ-Klasse
        ("integer", "integer"),
        ("bigint", "integer"),
        ("smallint", "integer"),
        # Numerik mit Präzision: Präzision ist unterhalb der Typ-Klasse
        ("numeric", "numeric"),
        ("real", "float"),
        ("double precision", "float"),
        # Zeit: mit/ohne Zeitzone ist unterhalb der Typ-Klasse
        ("timestamp with time zone", "timestamp"),
        ("timestamp without time zone", "timestamp"),
        ("date", "date"),
        ("time with time zone", "time"),
        ("time without time zone", "time"),
        # Rest
        ("boolean", "boolean"),
        ("uuid", "uuid"),
        ("jsonb", "json"),
        ("json", "json"),
        ("bytea", "bytea"),
        ("ARRAY", "array"),
        ("point", "point"),
    ],
)
def test_known_types_map_to_their_class(pg_type, expected):
    assert type_class(pg_type) == expected


def test_unknown_types_pass_through_unchanged():
    # Lieber ehrlich den DB-Typ zeigen als falsch klassifizieren
    assert type_class("tsvector") == "tsvector"
