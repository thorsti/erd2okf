"""Introspektion: liest die Struktur einer Live-DB auf Typ-Klassen-Ebene."""

from erd2okf.introspect import introspect


def test_reads_tables_with_columns_as_type_classes(db):
    db.execute(
        """
        CREATE TABLE widgets (
            id UUID PRIMARY KEY,
            label VARCHAR(50) NOT NULL,
            weight NUMERIC(8,2)
        )
        """
    )

    tables = introspect(db)

    assert [t.name for t in tables] == ["widgets"]
    cols = {c.name: c for c in tables[0].columns}
    assert set(cols) == {"id", "label", "weight"}
    assert cols["id"].type == "uuid"
    assert cols["id"].primary_key is True
    assert cols["id"].nullable is False
    assert cols["label"].type == "text"  # Typ-Klasse, nicht varchar(50)
    assert cols["label"].nullable is False
    assert cols["weight"].type == "numeric"
    assert cols["weight"].nullable is True
    assert cols["weight"].primary_key is False


def test_reads_foreign_keys_as_references(db):
    db.execute("CREATE TABLE owners (id UUID PRIMARY KEY)")
    db.execute(
        """
        CREATE TABLE pets (
            id UUID PRIMARY KEY,
            owner_id UUID NOT NULL REFERENCES owners(id) ON DELETE CASCADE
        )
        """
    )

    tables = {t.name: t for t in introspect(db)}

    owner_id = next(c for c in tables["pets"].columns if c.name == "owner_id")
    assert owner_id.references == "owners.id"


def test_reads_table_and_column_comments(db):
    db.execute("CREATE TABLE things (id UUID PRIMARY KEY, note TEXT)")
    db.execute("COMMENT ON TABLE things IS 'Alle Dinge.'")
    db.execute("COMMENT ON COLUMN things.note IS 'Freitext zum Ding.'")

    (things,) = introspect(db)

    assert things.comment == "Alle Dinge."
    cols = {c.name: c for c in things.columns}
    assert cols["note"].comment == "Freitext zum Ding."
    assert cols["id"].comment is None


def test_composite_primary_key_marks_all_members(db):
    db.execute(
        """
        CREATE TABLE readings (
            id BIGSERIAL,
            taken_at TIMESTAMPTZ NOT NULL,
            PRIMARY KEY (id, taken_at)
        )
        """
    )

    (readings,) = introspect(db)

    pk_cols = {c.name for c in readings.columns if c.primary_key}
    assert pk_cols == {"id", "taken_at"}
    cols = {c.name: c for c in readings.columns}
    assert cols["id"].type == "integer"  # bigserial -> bigint -> integer-Klasse
    assert cols["taken_at"].type == "timestamp"


def test_tables_and_columns_keep_stable_order(db):
    db.execute("CREATE TABLE zebra (b TEXT, a TEXT)")
    db.execute("CREATE TABLE apple (x TEXT)")

    tables = introspect(db)

    assert [t.name for t in tables] == ["apple", "zebra"]
    # Spalten in Definitionsreihenfolge, nicht alphabetisch
    assert [c.name for c in tables[1].columns] == ["b", "a"]
