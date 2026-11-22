# Geräteprüfung Feuerwehr – Agent Skill

Deutschsprachiger, quelloffener Ablauf für Geräteabfragen und begleitete Prüfungen mit dem MCP-Dienst der [Feuerwehr-Prüf-App](https://feuerwehr-pruefung.de). Funktioniert mit einem MCP-fähigen Agenten; die Anleitung setzt keine bestimmte Marke oder kostenpflichtige Lizenz voraus. Verfügbarkeit, Kontingente und Organisationsregeln des jeweiligen Clients gelten weiterhin.

Der Skill beschreibt den Ablauf. Der MCP-Connector stellt die Verbindung her. Anmeldung, Stationsrechte, Qualifikation, Berechtigung und persönliche Prüfungsfreigabe bleiben Aufgaben des Servers und der prüfenden Person.

## 1. Verbindung einrichten

| Umgebung | MCP-Adresse | Zweck |
|---|---|---|
| Anwendung | `https://feuerwehr-pruefung.de/mcp` | Eigene freigegebene Daten; Schreibfunktionen nur bei serverseitiger Freigabe |
| Preprod | `https://pp.feuerwehr-pruefung.de/mcp` | Abgestimmte Tests mit ausdrücklich dafür vorgesehenen Testdaten |

Ein vorhandenes Anwendungskonto und eine Stationsmitgliedschaft sind erforderlich. Der Skill richtet keine Konten, Pläne oder Berechtigungen ein. Preprod-Zugangsdaten werden separat durch den Betreiber vergeben und gehören nicht in öffentliche Issues oder Chats.

### Claude

1. Unter **Plugins** (neuere Oberfläche) bzw. **Customize → Connectors** einen benutzerdefinierten Web-Connector hinzufügen. Je nach Oberfläche heißt der Weg **Add custom connector** oder **Add → Custom → Web**. Die vollständige MCP-Adresse aus der Tabelle verwenden.
2. Falls angeboten: **Sign in now** und OAuth-Client **Register automatically** auswählen. Der Dienst verwendet dynamische Client-Registrierung (DCR) mit PKCE S256. **Use Claude’s published identity** (CIMD) ist derzeit nicht unterstützt. Kein eigenes Client-Geheimnis und keine festen Authorization-Header eintragen.
3. Im Browser mit dem bestehenden Konto der gewählten Anwendung anmelden und die gewünschten Rechte prüfen. Für Abfragen genügt Lesen. Schreibrechte nur für einen ausdrücklich vereinbarten Prüfablauf anfordern; ein OAuth-Schreibrecht aktiviert den serverseitigen Schreibschalter nicht.
4. Den Connector in einem neuen Chat einschalten. Bei einem Test nur den Preprod-Connector aktivieren, damit keine Verwechslung mit der Anwendung entsteht.

Claude dokumentiert aktuell einen benutzerdefinierten Connector für Free-Konten. In verwalteten Organisationen können Besitzerrechte erforderlich sein. Ein ausgegrauter Eintrag ist kein Hinweis auf einen Serverfehler: zuerst Konto, Organisation und Client-Oberfläche prüfen. Einen funktionierenden Connector nicht ungefragt löschen. Ist der einzige Free-Slot belegt, kann die Person nach bewusster Entscheidung den bisherigen Connector entfernen und den Test-Connector hinzufügen. Das verändert keine Anwendungsdaten. Anschließend lässt sich die ursprüngliche URL wieder einrichten; die aktuelle Anbieteroberfläche und deren Limits bleiben maßgeblich.

Quelle und aktuelle Oberfläche: [Claude: Custom Connectors](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp). Dokumentationsstand: 22. November 2026. Die Nennung eines Tarifs ist keine Bestätigung eines realen Tests auf diesem Tarif.

## 2. Skill installieren

### Claude: ZIP passend zur Oberfläche importieren

1. Unter [Releases](https://github.com/heffdev/feuerwehr-pruefung-skill/releases/latest) das passende ZIP herunterladen. Die allgemeine GitHub-Funktion „Download ZIP“ liefert den Quellcode und ist nicht das Importpaket.
2. Falls nötig, unter **Settings → Capabilities** die Dateierstellung/Codeausführung aktivieren (je nach Oberfläche **Create and edit files**). Organisationsrichtlinien bleiben maßgeblich.
3. Neue **Plugins**-Oberfläche mit **Add → Upload plugin**: **feuerwehr-pruefung-claude-plugin.zip** hochladen. Dieses Paket enthält ein minimales Plugin-Manifest und genau denselben Skill. Es richtet keinen zusätzlichen MCP-Connector ein und enthält keine Skripte oder Hooks.
   Ältere Oberfläche mit **Customize → Skills → + → Create skill → Upload a skill**: **feuerwehr-pruefung-skill.zip** hochladen. Die beiden Pakete sind Alternativen; nicht beide installieren. Falls die konkrete Oberfläche den Import ablehnt, den bereinigten Fehler melden; der Import ist vor dem realen Test noch nicht bestätigt.
4. Den Skill zusammen mit dem zuvor eingerichteten MCP-Connector verwenden.

Offizielle Anleitungen: [neue Plugins-Oberfläche](https://support.claude.com/en/articles/17740565-manage-plugins-skills-and-connectors-from-one-plugins-page), [Skills verwenden](https://support.claude.com/en/articles/12512180-use-skills-in-claude), [eigene Skills und ZIP-Struktur](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills), [Plugin-Archivformat](https://platform.claude.com/docs/en/manage-claude/plugins-api#upload-requirements). Das letzte Dokument beschreibt das Format der Plugin-Archive, nicht einen API-Zugang für individuelle Free-Konten.

### Andere Agenten

Die Datei [SKILL.md](skills/feuerwehr-pruefung/SKILL.md) zusammen mit ihrem Verzeichnis `references/` gemäß den Skill-Anweisungen des Clients installieren. Oder den Agenten bitten, diese öffentliche Anleitung zu lesen:

```text
Lies https://raw.githubusercontent.com/heffdev/feuerwehr-pruefung-skill/main/skills/feuerwehr-pruefung/SKILL.md
und die dort verlinkte Werkzeugreferenz. Verwende sie für die Geräteprüfung mit meinem bereits verbundenen MCP-Connector.
Führe zunächst nur pruefung_whoami aus und frage nach, falls die Station oder Umgebung unklar ist.
```

Das Lesen einer URL ist keine dauerhafte Installation und verbindet keinen MCP-Server. Falls der Client keine Skills unterstützt, können die Anweisungen als Kontext verwendet werden. OAuth und Werkzeugunterstützung müssen trotzdem im Client eingerichtet sein.

## 3. Erste Abfrage

```text
Nutze ausschließlich meinen Preprod-Connector. Rufe pruefung_whoami auf.
Welche Stationen kann ich verwenden? Starte noch keine Prüfung.
```

Weitere Beispiele:

- „Welche Geräte meiner Station sind in den nächsten 30 Tagen fällig?“
- „Zeige mir Checkliste und letzte Prüfungen für das Gerät mit dieser Inventarnummer: …“
- „Begleite mich durch eine Prüfung dieses ausdrücklich als Testgerät markierten Geräts. Frage nach echten Beobachtungen und stoppe vor meiner persönlichen Freigabe.“

Bei mehreren Stationen die gewünschte Station ausdrücklich wählen. Ist nur Lesen verfügbar, bleiben Abfragen möglich; der Skill umgeht keine gesperrten Schreibfunktionen.

## Prüfung und persönliche Freigabe

Der Agent darf nach ausdrücklichem Auftrag einen Entwurf vorbereiten und tatsächliche Angaben erfassen. Er darf keine Sichtprüfung, Messung, Unterschrift oder Verfahrensnachweise erfinden. Die prüfende Person kontrolliert die vollständigen Daten auf der Bestätigungsseite der Anwendung und bestätigt selbst mit ihrer bestehenden Anmeldung. Erst anschließend kann der Agent die exakt freigegebenen Daten einreichen. `confirm:true` ersetzt diese Freigabe nicht.

Die serverseitige Freigabe ist zehn Minuten gültig, einmalig und an Person, Station, Entwurf, Checksumme und vollständigen Dateninhalt gebunden. Änderungen erfordern eine erneute Prüfung und Freigabe. Fehlende Pläne, Qualifikationen oder Rechte sind in der Anwendung durch berechtigte Personen zu klären.

Keine Audiodateien oder Gesprächstranskripte an den MCP-Dienst übertragen. In den Prüfnachweisen nur die erforderlichen tatsächlichen Angaben speichern. Die Datenschutz- und Aufbewahrungseinstellungen des gewählten KI-Anbieters sind separat zu prüfen; dieser Skill konfiguriert sie nicht.

## Paket lokal bauen

Python 3.10 oder neuer, keine Zusatzpakete:

```console
python scripts/build_skill.py
```

Erzeugt beide Import-ZIPs und `dist/SHA256SUMS`. Das portable Skill-ZIP enthält ausschließlich `SKILL.md`, die Werkzeugreferenz und die MIT-Lizenz unter dem Ordner `feuerwehr-pruefung/`. Das Claude-Plugin-ZIP enthält dasselbe unter `skills/feuerwehr-pruefung/` sowie das minimale Manifest und die Lizenz; es bündelt keine MCP-Konfiguration. Keine Zugangsdaten oder Anwendungsdateien einpacken. Verhaltensprüfungen stehen in [evals/scenarios.md](evals/scenarios.md).

## Lizenz und Grenzen

[MIT](LICENSE) gilt für die ursprünglichen Anleitungen und Hilfsdateien dieses Repositorys. Die private Anwendung, Dienstdaten, Marken und externe Regelwerke werden dadurch nicht unter MIT gestellt. Der Skill verleiht keine Prüfqualifikation und ersetzt weder die tatsächliche Prüfung noch die Verantwortung der prüfenden Person. Probleme bitte ohne Passwörter, Tokens oder personenbezogene Prüfdaten melden.
