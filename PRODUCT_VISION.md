Produktvision: Schema-Doku als generierte OKF-Files
Scope
Diese Vision beschreibt, wie das Datenbankschema als generierte Markdown-Files im OKF-Format im Repo landet und aktuell bleibt. Die Semantik-Pflege (Freitext pro Tabelle) und die Ausbaustufe (Typ-Fingerprints, Rollout über mehrere Cluster) sind hier als Richtung genannt, nicht als Teil des ersten Wurfs. Was der erste Wurf beweisen muss, steht unter "Erfolgskriterien PoC".
Problem
Schema-Doku liegt in proprietären Formaten in Confluence, auf Netzlaufwerken oder auf der Platte von irgendwem. Niemand pflegt sie. Die wenigsten haben je damit gearbeitet, sie musste nur existieren. In einer Welt, in der man das Schema nicht mehr wälzt sondern ein LLM fragt, ist tote Doku nicht nur nutzlos. Sie ist gefährlich, weil das Modell sie selbstbewusst falsch konsumiert.
Idee
Das Schema wird aus der Live-DB generiert und als OKF-Markdown pro Tabelle im Repo abgelegt. Eine Datei pro Tabelle, Struktur im Frontmatter, Semantik im Freitext-Body. Die Generierung hängt an der Migration (Alembic), nicht an Disziplin. Ein Drift-Check in der CI ist der Backstop, falls jemand am Hook vorbei direkt an der DB schraubt.
Kriterien
Woran wir eine gute Lösung hier messen, bevor wir sie empfehlen:

Aktualität ohne Disziplin: die Doku hält sich selbst aktuell, nicht durch Erinnerung.
Billig prüfbar: Drift auf der relevanten Ebene ist mit wenig Aufwand erkennbar.
Maschinenlesbar: ein Agent konsumiert die Struktur ohne Interpretationsschicht.
Vendor-neutral: Markdown und YAML im Repo, kein Tool-Lock-in, ein Ordner den man löschen kann.
Ehrliche Zusage: grün bedeutet etwas Definiertes, nicht "wird schon passen".

Nicht-Ziele

Kein Ersatz für einen Catalog. Die DB bleibt System of Record, die Files sind der versionierte Snapshot.
Kein Handpflegen der Struktur. Handgepflegt rottet sie, und gelogene Doku ist schlechter als keine.
Nicht jeden Diff fangen. varchar(10) auf varchar(20) ist egal. Rename und Drop nicht.
Kein Long-running-Sidecar als Pflicht. Ein post-migrate Job oder ein CI-Schritt reicht.

Erfolgskriterien PoC
Der PoC ist erfolgreich, wenn er auf einer DB:

jede Tabelle als Datei abbildet (Namens-Set DB gleich Namens-Set Files)
add, drop und rename von Tabellen und Spalten rot färbt
bewusst nichts unterhalb der Typ-Klasse prüft

Grün heißt dann: keine strukturell relevante Drift. Nicht: Schema identisch. Das ist die einzige Zusage, die der PoC macht.
Der PoC ist gescheitert, wenn ein gelöschtes Feld grün durchläuft, oder wenn die Semantik bei einer Regeneration verloren geht.
Mehrwert, wenn es steht

Menschen: aktuelles ERD im Repo, im PR reviewbar, statt PNG von 2023.
Agenten: verlässlicher Schema-Kontext. "Welche User in Gruppe xy aber nicht z" statt komplettem Schema-Dump.
Betrieb: Drift wird sichtbar, bevor jemand darüber stolpert.

Richtung danach
Fingerprints pro Tabelle für die Typ-Ebene. Merge-Strategie für den Freitext-Body, damit Regeneration die Semantik nicht plattmacht. Rollout über C1/C2/C3. Alles erst, wenn der erste Wurf sich als tragfähig zeigt.