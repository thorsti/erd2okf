"""Liest die Struktur einer Live-Postgres auf Typ-Klassen-Ebene.

Die DB bleibt System of Record; hier entsteht nur der Snapshot.
"""

from dataclasses import dataclass, field

import psycopg

from erd2okf.typeclass import type_class

# Werkzeug-Buchhaltung, keine Schema-Doku
DEFAULT_EXCLUDE = frozenset({"alembic_version"})


@dataclass
class Column:
    name: str
    type: str
    nullable: bool
    primary_key: bool = False
    references: str | None = None
    comment: str | None = None


@dataclass
class Table:
    name: str
    columns: list[Column] = field(default_factory=list)
    comment: str | None = None


_COLUMNS_SQL = """
SELECT c.table_name,
       c.column_name,
       c.data_type,
       c.udt_name,
       c.is_nullable = 'YES' AS nullable,
       col_description(format('%%I.%%I', c.table_schema, c.table_name)::regclass,
                       c.ordinal_position) AS comment
FROM information_schema.columns c
JOIN information_schema.tables t
  ON t.table_schema = c.table_schema AND t.table_name = c.table_name
WHERE c.table_schema = %(schema)s AND t.table_type = 'BASE TABLE'
ORDER BY c.table_name, c.ordinal_position
"""

_TABLE_COMMENTS_SQL = """
SELECT t.table_name,
       obj_description(format('%%I.%%I', t.table_schema, t.table_name)::regclass,
                       'pg_class') AS comment
FROM information_schema.tables t
WHERE t.table_schema = %(schema)s AND t.table_type = 'BASE TABLE'
"""

_PRIMARY_KEYS_SQL = """
SELECT tc.table_name, kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON kcu.constraint_name = tc.constraint_name
 AND kcu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = %(schema)s
"""

_FOREIGN_KEYS_SQL = """
SELECT rel.relname AS table_name,
       a.attname AS column_name,
       frel.relname AS ref_table,
       af.attname AS ref_column
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
JOIN pg_class frel ON frel.oid = con.confrelid
JOIN unnest(con.conkey) WITH ORDINALITY AS ck(attnum, ord) ON true
JOIN unnest(con.confkey) WITH ORDINALITY AS cfk(attnum, ord) ON cfk.ord = ck.ord
JOIN pg_attribute a ON a.attrelid = con.conrelid AND a.attnum = ck.attnum
JOIN pg_attribute af ON af.attrelid = con.confrelid AND af.attnum = cfk.attnum
WHERE con.contype = 'f' AND con.connamespace = %(schema)s::regnamespace
"""


def introspect(
    conn: psycopg.Connection,
    schema: str = "public",
    exclude: frozenset[str] | set[str] = DEFAULT_EXCLUDE,
) -> list[Table]:
    """Alle Basistabellen eines Schemas, sortiert nach Name."""
    params = {"schema": schema}
    table_comments = dict(conn.execute(_TABLE_COMMENTS_SQL, params).fetchall())
    pk = set(map(tuple, conn.execute(_PRIMARY_KEYS_SQL, params).fetchall()))
    fk = {
        (t, c): f"{rt}.{rc}"
        for t, c, rt, rc in conn.execute(_FOREIGN_KEYS_SQL, params).fetchall()
    }

    tables: dict[str, Table] = {}
    for tname, cname, data_type, udt_name, nullable, comment in conn.execute(
        _COLUMNS_SQL, params
    ):
        if tname in exclude:
            continue
        table = tables.setdefault(
            tname, Table(name=tname, comment=table_comments.get(tname))
        )
        pg_type = udt_name if data_type == "USER-DEFINED" else data_type
        table.columns.append(
            Column(
                name=cname,
                type=type_class(pg_type),
                nullable=nullable,
                primary_key=(tname, cname) in pk,
                references=fk.get((tname, cname)),
                comment=comment,
            )
        )
    return [tables[name] for name in sorted(tables)]
