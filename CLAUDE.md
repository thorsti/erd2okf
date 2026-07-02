# Leitplanken für dieses Repo

## tests/test_poc_criteria.py ist der Vertrag

Die Datei bildet die PoC-Erfolgskriterien aus PRODUCT_VISION.md wörtlich ab —
inklusive der Scheiter-Kriterien. Sie wird **nie an eine Implementierung
angepasst**. Wird einer dieser Tests rot, ist das Design falsch, nicht der Test.
Ein "angepasster" Vertragstest streicht still ein Scheiter-Kriterium der Vision.

## Backlinks / Cross-Links (offene Design-Frage aus dem README)

OKF baut seinen Knowledge Graph über Markdown-Links zwischen Files. Wer das
implementiert, läuft in genau eine Falle: **Links, die in den Freitext-Body
generiert werden, brechen das Invariant "der Body wird bei Regeneration nie
angefasst"** — und `test_semantics_survive_regeneration` wird das melden.
Das ist dann kein Test-Problem.

Saubere Lösungen:

- `references` im Frontmatter als relative File-Pfade (z. B. `./vehicle_fleets.md`), oder
- eine klar markierte, generierte Sektion **vor** dem handgepflegten Body
  (z. B. zwischen HTML-Kommentar-Markern), die `generate` besitzt und neu
  schreibt, während alles danach unangetastet bleibt.

Die Wahl zwischen beiden ist eine bewusste Design-Entscheidung mit Trade-offs
(echte Spec-Graph-Mechanik vs. Einfachheit des Formats) — sie soll explizit
fallen und begründet werden, nicht nebenbei als Fix für einen rot gewordenen Test.
