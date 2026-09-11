# REMKO HTTP

[![GitHub License](https://img.shields.io/github/license/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http)
[![GitHub Release](https://img.shields.io/github/v/release/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)

Home Assistant Custom Integration für REMKO Wärmepumpen mit lokaler HTTP-/CGI-Schnittstelle.

Die Integration kommuniziert direkt mit der REMKO Steuerung über das lokale Netzwerk. Es wird weder ein MQTT-Broker noch eine Cloud-Verbindung benötigt.

> 🇬🇧 English: [README.en.md](README.en.md)

## Features

- Lokale Kommunikation über HTTP/CGI
- Keine Cloud-Verbindung erforderlich
- Kein MQTT-Broker erforderlich
- Einrichtung über die Home-Assistant-Oberfläche
- Unterstützung von Home Assistant Config Flow
- Betriebs- und Messwerte als Home-Assistant-Entitäten
- HACS-Installation möglich
- Kommunikation ohne Benutzername und Passwort bei unterstützten Geräten

## Supported Devices

| Device / Firmware | Status |
|---|---|
| REMKO Wärmepumpe mit Firmware 4.25 | ✅ Getestet |
| Andere Firmware-Versionen | ❓ Ungetestet |

Die Integration wurde mit REMKO Systemen auf Basis von Firmware 4.25 entwickelt und getestet.
Andere Firmware-Versionen können eine abweichende HTTP-/CGI-Schnittstelle verwenden und sind daher nicht automatisch kompatibel.
Feedback zu weiteren Modellen und Firmware-Versionen ist willkommen.

## Voraussetzungen

- Home Assistant
- REMKO Wärmepumpe mit unterstützter Firmware
- Netzwerkverbindung zwischen Home Assistant und Wärmepumpe
- Erreichbare lokale HTTP-/CGI-Schnittstelle

Eine feste IP-Adresse bzw. DHCP-Reservierung für die Wärmepumpe wird empfohlen.

## Installation

### HACS

1. HACS in Home Assistant öffnen.
2. Zu **Integrationen** wechseln.
3. **⋮ → Benutzerdefinierte Repositories** öffnen.
4. Folgendes Repository hinzufügen:

   `https://github.com/fuchsi585/remko_http`

5. Repository-Typ **Integration** auswählen.
6. **REMKO HTTP** installieren.
7. Home Assistant neu starten.

### Manuell

Das Verzeichnis

`custom_components/remko_http`

in das Home-Assistant-Konfigurationsverzeichnis kopieren:

```text
/config/custom_components/remko_http/
```

Anschließend Home Assistant neu starten.

## Konfiguration

Nach der Installation:

1. **Einstellungen → Geräte & Dienste** öffnen.
2. **Integration hinzufügen** auswählen.
3. Nach **REMKO HTTP** suchen.
4. Die lokale IP-Adresse der REMKO Wärmepumpe eingeben.
5. Konfiguration abschließen.

Beispiel:

```text
192.168.1.50
```

Die Verbindung erfolgt anschließend direkt von Home Assistant zur REMKO Steuerung.

## Kommunikation

```text
Home Assistant
      │
      │ HTTP / CGI
      ▼
REMKO Wärmepumpe
```

Die Integration verwendet die lokale Web-/CGI-Schnittstelle der REMKO Steuerung.
Es werden keine externen Server für die Kommunikation benötigt.

## Entitäten

- Temperaturen
- Betriebszustände
- Warmwasserwerte
- Leistungswerte
- Betriebsparameter
- weitere von der Steuerung bereitgestellte Messwerte

## Fehlerbehebung

### Wärmepumpe nicht erreichbar

Folgende Punkte prüfen:

1. Ist die Wärmepumpe eingeschaltet?
2. Ist die Wärmepumpe im Netzwerk erreichbar?
3. Ist die konfigurierte IP-Adresse korrekt?
4. Befinden sich Home Assistant und Wärmepumpe im selben Netzwerk?
5. Wird die Verbindung durch Firewall oder VLAN-Regeln blockiert?

### Keine Daten

Wenn die Verbindung hergestellt wird, aber keine Werte gelesen werden:

- Firmware-Version prüfen
- IP-Adresse prüfen
- HTTP-/CGI-Schnittstelle prüfen
- Home-Assistant-Logs prüfen
- Modell und Firmware bei einem Issue angeben

### Andere Firmware

Die Implementierung basiert auf der bei Firmware 4.25 beobachteten HTTP-/CGI-Kommunikation.

Bei neueren Firmware-Versionen kann sich die Schnittstelle geändert haben. In diesem Fall können Datenstrukturen, Endpunkte oder Abfrageparameter abweichen.

## Technische Details

- Plattform: Home Assistant
- Protokoll: HTTP
- Schnittstelle: CGI
- Netzwerk: lokal
- MQTT: nicht erforderlich
- Cloud: nicht erforderlich
- Getestete Firmware: 4.25

Die Kommunikation erfolgt direkt zwischen Home Assistant und der REMKO Steuerung.

## Entwicklung

Pull Requests und Issues sind willkommen.

## Danksagung

Vielen Dank an **Altrec** für die Inspiration und die Vorarbeit rund um die Integration von REMKO Wärmepumpen in Home Assistant. Ebenso vielen Dank an die Home-Assistant-Community für den Austausch und die zahlreichen Erkenntnisse.

## Disclaimer

Dieses Projekt ist nicht offiziell mit REMKO verbunden und wird nicht von REMKO unterstützt.

Die Verwendung erfolgt auf eigene Verantwortung.

## Lizenz

MIT License

## Autor

Entwickelt von [fuchsi585](https://github.com/fuchsi585).