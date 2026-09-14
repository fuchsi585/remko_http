# Modernes REMKO-Dashboard

Das Dashboard in [`remko_dashboard.yaml`](remko_dashboard.yaml) ist eine moderne,
responsive Alternative zur ursprünglichen REMKO-Wiki-Vorlage. Es verwendet nur
Home-Assistant-Bordmittel und benötigt weder `button-card` noch
`text-divider-row`.

## Installation

1. In Home Assistant **Einstellungen → Dashboards → Dashboard hinzufügen** öffnen.
2. Ein neues Dashboard erstellen und anschließend **Dashboard bearbeiten →
   Drei-Punkte-Menü → Raw-Konfigurationseditor** wählen.
3. Den gesamten Inhalt aus `remko_dashboard.yaml` einfügen und speichern.
4. Falls Home Assistant beim Einrichten andere Entitäts-IDs vergeben hat, die
   betroffenen IDs im YAML ersetzen. Die tatsächliche ID steht unter
   **Einstellungen → Geräte & Dienste → REMKO HTTP → Wärmepumpe**.

Die Entitäts-IDs des Dashboards müssen ggfs. aktuallisiert werden.

## Hinweise

- Die Karten für Tages- und Monatsenergie setzen voraus, dass die entsprechenden
  Integrationsentitäten aktiviert sind.
- Der Aktionsknopf zum einmaligen Aufheizen ist nur verfügbar, wenn die Anlage
  diese Aktion aktuell zulässt.
- Grenzwerte der beiden Temperaturanzeigen und der Leistungsanzeige können direkt
  im YAML an die eigene Anlage angepasst werden.
