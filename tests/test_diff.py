"""Drift-Check: die einzige Zusage des PoC.

Rot: add, drop, rename von Tabellen und Spalten, Wechsel der Typ-Klasse.
Grün: alles unterhalb davon — bewusst.
"""

from erd2okf.diff import diff
from erd2okf.introspect import Column, Table


def _t(name, **cols):
    return Table(
        name=name,
        columns=[Column(name=c, type=t, nullable=True) for c, t in cols.items()],
    )


def test_identical_schemas_are_green():
    assert diff([_t("users", id="uuid")], [_t("users", id="uuid")]) == []


def test_table_only_in_db_is_red():
    findings = diff([_t("users", id="uuid"), _t("audit_log", id="uuid")],
                    [_t("users", id="uuid")])

    assert [(f.kind, f.table) for f in findings] == [("table_added", "audit_log")]


def test_table_only_in_files_is_red():
    """Ein Drop darf nie grün durchlaufen — das Scheiter-Kriterium des PoC."""
    findings = diff([], [_t("users", id="uuid")])

    assert [(f.kind, f.table) for f in findings] == [("table_removed", "users")]


def test_column_added_in_db_is_red():
    findings = diff([_t("users", id="uuid", email="text")], [_t("users", id="uuid")])

    assert [(f.kind, f.table, f.column) for f in findings] == [
        ("column_added", "users", "email")
    ]


def test_column_dropped_in_db_is_red():
    findings = diff([_t("users", id="uuid")], [_t("users", id="uuid", email="text")])

    assert [(f.kind, f.table, f.column) for f in findings] == [
        ("column_removed", "users", "email")
    ]


def test_rename_shows_as_drop_plus_add():
    findings = diff([_t("users", id="uuid", mail="text")],
                    [_t("users", id="uuid", email="text")])

    assert {(f.kind, f.column) for f in findings} == {
        ("column_added", "mail"),
        ("column_removed", "email"),
    }


def test_type_class_change_is_red():
    findings = diff([_t("users", id="uuid", age="text")],
                    [_t("users", id="uuid", age="integer")])

    assert [(f.kind, f.table, f.column) for f in findings] == [
        ("type_changed", "users", "age")
    ]
    assert "integer" in findings[0].detail and "text" in findings[0].detail


def test_below_type_class_is_deliberately_green():
    """Nullable/PK/FK sind nicht Teil der Zusage des PoC."""
    db = Table("users", columns=[
        Column(name="id", type="uuid", nullable=False, primary_key=True),
    ])
    doc = Table("users", columns=[
        Column(name="id", type="uuid", nullable=True, primary_key=False),
    ])

    assert diff([db], [doc]) == []


def test_findings_have_readable_messages():
    (finding,) = diff([], [_t("users", id="uuid")])

    assert "users" in str(finding)
