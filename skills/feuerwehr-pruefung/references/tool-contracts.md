# Öffentliche Werkzeugreferenz

Diese Anleitung beschreibt die öffentlich angebotenen Funktionen. Die im verbundenen Client tatsächlich entdeckten Werkzeuge und Schemas sind maßgeblich. Clientpräfixe bei Werkzeugnamen sind möglich. Keine eigenen REST-Endpunkte oder Verwaltungswerkzeuge erfinden.

## Lesewerkzeuge

`station_id` ist bei stationsgebundenen Aufrufen eine autorisierte positive ganze Zahl; bei mehreren Mitgliedschaften ausdrücklich auswählen. `identifier` ist die Gerätekennung, 2–50 Zeichen aus Buchstaben, Ziffern, Bindestrich oder Unterstrich, beginnend mit Buchstabe oder Ziffer.

| Werkzeug | Argumente | Antwort verwenden für |
|---|---|---|
| `pruefung_whoami` | keine | Aktuelle Person (`user.full_name`), Mitgliedschaften, Scopes und Entitlement; keine Schreibfreigabe allein daraus ableiten |
| `pruefung_list_due` | optional `station_id`, `within_days` 0–365, `category`, `limit` 1–50, `offset` | Fällige Geräte; begrenzt paginieren, Kategoriecode aus dem Kontext verwenden |
| `pruefung_get_equipment` | `identifier`; optional `station_id` | Gerät, Plan oder `plan:null`, Berechtigung und historischer Kontext |
| `pruefung_get_checklist` | `identifier`; optional `station_id`, `inspection_kind` | Autoritative Legacy-/Compliance-Checkliste einschließlich Checksumme, Metadaten und Anforderungen |
| `pruefung_get_history` | `identifier`; optional `station_id`, `limit` 1–50 | Historische Prüfungen und vorhandene Evidenzhashes; kein `offset`-Argument |

Prüfarten: `regular`, `load`, `initial`, `event`. Historische Zeitstempel oder Nachweise können fehlen; fehlende Daten nicht ergänzen. Ein lesbares Legacy-Template garantiert keinen für eine neue Compliance-Prüfung gültigen Plan.

## Schreibwerkzeuge

Nur verfügbar, wenn der Server Schreibfunktionen aktiviert und der angemeldete Zugang `pruefung.write` besitzt. Aktuelle Mitgliedschaft, Rolle, Qualifikation, Grant, Entitlement und Compliance werden unabhängig geprüft. `pruefung.read` bleibt für Lesewerkzeuge erforderlich.

### `pruefung_start_inspection`

Erforderlich: `identifier`, `inspection_kind`. Optional: `station_id`, `client` als Objekt. Erzeugt nur einen Entwurf, keine abgeschlossene Prüfung. Die Antwort liefert `draft_id`, `expires_at` und `checklist` mit `checksum` sowie den anzuwendenden Punkten.

### `pruefung_set_results`

Erforderlich: `draft_id`, `results` als Array. Jeder Ergebnisdatensatz nutzt die vom Server gelieferte `template_item_id` und die vorgesehenen Felder `passed` (true/false/null), `value_entered` (Zeichenfolge), `notes` (Zeichenfolge). Typ und Werte gemäß Checkliste erfassen; unbekannte IDs nicht erfinden.

- Anwendbare boolesche Punkte: `passed:true` oder `passed:false`; tatsächliche Mängel in `notes` beschreiben.
- Anwendbare numerische Punkte (`value`/`measurement`): ebenfalls die tatsächliche Bewertung true/false; `value_entered` enthält nur die Zahl als Zeichenfolge (Dezimalpunkt oder -komma), keine Einheit im Zahlenfeld. Einheit gemäß Checkliste nennen; die tatsächlich angewandte Grenze und Bewertungsgrundlage müssen in `notes` stehen. Ein Messwert mit `passed:null` wäre N/A und wird abgelehnt.
- Textpunkte: `passed:null` und nichtleerer tatsächlicher Text in `value_entered`.
- Zulässiges N/A bei Nicht-Textpunkten: `passed:null`, `value_entered:""` und eine tatsächliche Begründung in `notes`; keinen vorhandenen Messwert als N/A kennzeichnen.

Zusätzliche vorbereitete Angaben: `result`, `procedure_evidence`, `signature_name`, `notes`, `ladder_measurements` als Objekt und `language` (`de`/`en`). Die nötigen Messfelder ergeben sich aus den konkreten Anforderungen; keine generische Messstruktur erfinden. Alle erforderlichen Daten vor der Freigabe speichern.

Gesamtresultate: `ok`, `monitor`, `repair`, `retired`. Ein ausgefallener Pflichtpunkt kann eine strengere Entscheidung erfordern. Ein „reparieren“-Ergebnis nicht wählen, wenn die anwendbaren Regeln Aussonderung verlangen.

Antwortfelder: `draft_id`, `received`, `outstanding`, `warnings`. Noch fehlende Angaben abarbeiten. Es gibt hier kein Feld `confirmation_url`.

### Persönliche Freigabe

Im bekannten Anwendungshost `/mcp-confirm-inspection.php?draft_id=…` öffnen. Die Person bestätigt selbst mit ihrer Anwendungssitzung. Es gibt kein MCP-Werkzeug zum Erzeugen dieser Freigabe. Keine automatisierte Anmeldung oder Bestätigung durch den Agenten.

### `pruefung_submit`

Erforderlich: `draft_id`, `result`, `procedure_evidence`, `signature_name`, `confirm`, `checklist_checksum`, `idempotency_key`. Optional: `language`. Die übrigen vollständigen Prüfdaten wurden zuvor im Entwurf gespeichert und sind Teil der Freigabebindung. Die wiederholten Felder müssen exakt zum freigegebenen Entwurf passen.

- `confirm:true` drückt die Absicht aus, ersetzt aber keine serververifizierte persönliche Freigabe.
- `checklist_checksum`: unverändert aus der autoritativen Checkliste, maximal 64 Zeichen.
- `idempotency_key`: für diesen Einreichungsvorgang einmalig erzeugen, z. B. UUID, maximal 64 Zeichen; bei unklarem Ausgang mit demselben Inhalt wiederverwenden.
- `procedure_evidence`: tatsächlicher erforderlicher Verfahrensnachweis, kein Gesprächstranskript.
- `signature_name`: tatsächlicher vollständiger Name der angemeldeten prüfenden Person.

Erfolg enthält `inspection_id`, `result`, `next_due`, `evidence_sha256` und `pdf_available`. Nur vorhandene Daten berichten. Die Evidenzversiegelung und die atomare Speicherung erfolgen serverseitig.

## Umgang mit Ablehnungen

| Situation / mögliche Codes | Verhalten |
|---|---|
| `station_required` | Nach autorisierter Station fragen |
| `station_not_found`, `equipment_not_found` | Kennung und eigene Stationswahl klären; keine fremden Geräte enumerieren |
| `insufficient_scope`, `forbidden_role`, `no_authorization` | Stoppen, nötige Rechte/Qualifikation erklären; keine alternativen Zugangsdaten suchen |
| `plan_missing` | Berechtigte Person muss den Plan in der Anwendung pflegen |
| `confirmation_required` | Vollständige Daten erneut persönlich im ersten System bestätigen lassen |
| `checklist_changed` | Anforderungen neu laden, Unterschiede prüfen, erneut freigeben lassen |
| `draft_expired`, `draft_not_found`, `already_submitted` | Status/Historie klären, nicht blind neuen Entwurf einreichen |
| `procedure_evidence_required`, `value_out_of_range`, `mandatory_item_failed`, `retire_required`, `invalid_results` | Tatsächliche Angaben und konkrete Anforderungen prüfen; keine Werte zur Annahme erfinden |
| Entitlement-/Abrechnungsfehler | Berechtigte Person auf Kontoverwaltung verweisen; Abfragen nutzen, soweit erlaubt |
| `rate_limited` | Wartehinweis respektieren, keine parallelen Wiederholungen zur Umgehung |

Dies ist keine abschließende Liste. Ein unbekanntes oder nicht angebotenes Werkzeug darf nicht durch direkte Endpunktaufrufe ersetzt werden. Bei unklarem Fehler die konkrete Aktion stoppen und einen bereinigten Fehlerbericht anbieten.
