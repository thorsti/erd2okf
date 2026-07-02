# erd2okf

Postgres-Schema als generierte OKF-Markdown-Files im Repo — eine Datei pro Tabelle,
Struktur im YAML-Frontmatter, Semantik im Freitext-Body. Mit Drift-Check als CI-Backstop.

Warum: Schema-Doku in Confluence oder auf Netzlaufwerken pflegt niemand. In einer Welt,
in der ein LLM das Schema konsumiert, ist tote Doku gefährlich, weil das Modell sie
selbstbewusst falsch konsumiert. Hier wird die Doku aus der Live-DB generiert — Aktualität
hängt an der Migration, nicht an Disziplin. Details in [PRODUCT_VISION.md](PRODUCT_VISION.md).

## Benutzung

```bash
# Nach der Migration (z. B. als post-migrate Hook an Alembic):
erd2okf generate --dsn postgresql://... --out docs/schema

# In der CI, als Backstop gegen Schrauben an der DB vorbei:
erd2okf check --dsn postgresql://... --dir docs/schema
```

`check` liefert Exit-Code 0 (grün) oder 1 (Drift) und benennt jeden Befund:

```
DRIFT — 2 Befund(e):
  - Spalte vehicles.status existiert in den Files, aber nicht in der DB
  - Spalte shipments.weight_kg: Typ-Klasse dokumentiert als numeric, in der DB text
```

## Das Format

Ein File pro Tabelle ([komplettes Beispiel](examples/schema/), generiert aus
[data/test-model.sql](data/test-model.sql)):

```markdown
---
okf: 1
table: vehicles
columns:
- name: id
  type: uuid
  nullable: false
  primary_key: true
- name: fleet_id
  type: uuid
  nullable: false
  references: vehicle_fleets.id
---

Stammdaten für Fahrzeuge aller Art. Der Typ bestimmt, welche Sub-Details existieren.
```

- **Frontmatter** wird bei jeder Generierung aus der DB neu geschrieben. Die DB ist
  System of Record; hand-editieren lohnt nicht, es wird überschrieben.
- **Body** ist Freitext für Semantik. Er wird beim ersten Wurf aus `COMMENT ON TABLE`
  gesät und bei Regenerationen **nie angefasst** — hier wächst das Wissen, das nicht
  in der DB steht.
- Spalten-Comments aus der DB landen als `description` im Frontmatter.
- Files zu gelöschten Tabellen werden entfernt (die Historie hält git),
  fremde `.md` im Ordner (z. B. ein README) bleiben unberührt.

## Was grün bedeutet

Grün heißt: **keine strukturell relevante Drift**. Nicht: Schema identisch.

| Rot | Grün (bewusst) |
|---|---|
| Tabelle hinzugefügt / gelöscht / umbenannt | `varchar(10)` → `varchar(20)` |
| Spalte hinzugefügt / gelöscht / umbenannt | `numeric(8,2)` → `numeric(12,4)` |
| Typ-Klasse gewechselt (`numeric` → `text`) | `timestamp` mit ↔ ohne Zeitzone |
| | Nullability, Constraints, Indizes |

Geprüft wird auf Typ-Klassen-Ebene: `varchar`/`char`/`text` sind `text`,
`smallint`/`int`/`bigint` sind `integer`, usw. — siehe
[typeclass.py](src/erd2okf/typeclass.py). Ein Rename erscheint als drop + add
und färbt damit immer rot.

## Entwicklung

```bash
uv run pytest
```

Die Tests starten selbst eine Postgres per Docker. Alternativ zeigt
`ERD2OKF_TEST_DSN` auf eine laufende Instanz (so macht es die CI).
Die PoC-Erfolgskriterien aus der Vision sind wörtlich als Tests abgebildet:
[tests/test_poc_criteria.py](tests/test_poc_criteria.py).

## Richtung danach

Nicht Teil dieses ersten Wurfs, in der Vision als Richtung genannt:
Typ-Fingerprints pro Tabelle, Merge-Strategie für den Body, Rollout über mehrere Cluster.
