"""Schreibt den OKF-Ordner und hält ihn synchron zur DB-Struktur.

Frontmatter wird immer aus der DB neu geschrieben, der Freitext-Body
bleibt bei Regeneration unangetastet. Files zu gelöschten Tabellen
werden entfernt (die Historie hält git).
"""

from pathlib import Path

from erd2okf.introspect import Table
from erd2okf.okf import parse, render


def _existing_okf_files(out_dir: Path) -> dict[str, Path]:
    """Alle OKF-Files im Ordner, nach Tabellenname. Fremde .md bleiben außen vor."""
    found = {}
    for path in out_dir.glob("*.md"):
        try:
            table, _ = parse(path.read_text())
        except (ValueError, KeyError):
            continue
        found[table.name] = path
    return found


def generate(tables: list[Table], out_dir: Path) -> None:
    """Ein OKF-File pro Tabelle; Bodies bestehender Files bleiben erhalten."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = _existing_okf_files(out_dir)

    for table in tables:
        body = None
        previous = existing.pop(table.name, None)
        if previous is not None:
            _, body = parse(previous.read_text())
        (out_dir / f"{table.name}.md").write_text(render(table, body=body))

    for orphan in existing.values():
        orphan.unlink()
