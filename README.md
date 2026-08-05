# remko_http

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Firmware](https://img.shields.io/badge/firmware-4.25-orange.svg)](https://github.com/fuchsi585/remko_http)
[![Home Assistant](https://img.shields.io/badge/platform-Home%20Assistant-41BDF5.svg)](https://www.home-assistant.io/)
[![HACS Installations](https://img.shields.io/endpoint?url=https://hacs-badges.vercel.app/api/badges/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http)   

> **Eine schlanke Home Assistant Custom Integration für Remko Wärmepumpen (Firmware 4.25).**
> *Direkter Datenabruf über die lokale HTTP-Schnittstelle – ganz ohne MQTT-Broker und ohne Passwort.*

## 📖 Inhaltsverzeichnis

- [Über das Projekt](#-über-das-projekt)
- [Warum diese Integration?](#-warum-diese-integration)
- [Voraussetzungen](#-voraussetzungen)
- [Installation](#-installation)
- [Konfiguration](#-konfiguration)
- [Verfügbare Daten](#-verfügbare-daten)
- [Fehlerbehebung](#-fehlerbehebung)
- [Lizenz](#-lizenz)

## 🚀 Über das Projekt

**remko_http** liest Betriebsdaten deiner Remko Wärmepumpe direkt aus dem lokalen Netzwerk aus. Es nutzt die eingebaute Web-Schnittstelle (CGI) der Firmware 4.25.

Das Besondere: Da diese Firmware-Version im lokalen Netz keine Authentifizierung für den Datenabruf verlangt, ist die Integration extrem ressourcenschonend und einfach einzurichten. Es werden weder Benutzername noch Passwort benötigt.

## ⚖️ Warum diese Integration?

| Feature | **remko_http** (Dieses Projekt) | MQTT-Lösungen (ab FW 4.26+) |
| :--- | :--- | :--- |
| **Protokoll** | HTTP (CGI) | MQTT |
| **Firmware** | **4.25** (und ältere) | 4.26, 4.27, 4.28+ |
| **Authentifizierung** | **Keine erforderlich** 🎉 | Benutzername & Passwort nötig |
| **Zusatzsoftware** | Keine (Direktverbindung) | MQTT Broker (Mosquitto) nötig |
| **Einrichtung** | Nur IP-Adresse eingeben | Komplexe Bridge-Konfiguration |

## 📋 Voraussetzungen

- Eine Remko Wärmepumpe mit der **Firmware-Version 4.25**.
- Die Wärmepumpe muss im gleichen lokalen Netzwerk wie Home Assistant sein.
- Die **IP-Adresse** der Wärmepumpe muss bekannt und fest (oder per DHCP-Reservierung) zugewiesen sein.
- **Keine** Zugangsdaten notwendig.

## 📦 Installation

### Option A: HACS (Empfohlen)

1. Öffne HACS in Home Assistant.
2. Gehe zu "Integrationen" -> Menü (3 Punkte) -> "Benutzerdefinierte Repositorys".
3. Füge die URL dieses Repositories hinzu und wähle "Integration".
4. Suche nach "Remko HTTP", lade es herunter und starte Home Assistant neu.

### Option B: Manuell

1. Lade den Ordner `custom_components/remko_http` herunter.
2. Verschiebe ihn in dein Home Assistant Verzeichnis unter `config/custom_components/`.
3. Starte Home Assistant neu.

```bash
# Beispiel via SSH
cd /config/custom_components
git clone https://github.com/dein-username/remko_http.git   
```

## ⚙️ Konfiguration

Die Einrichtung erfolgt komplett über die Benutzeroberfläche:

1. Gehe zu **Einstellungen** -> **Geräte & Dienste**.
2. Klicke auf **Integration hinzufügen**.
3. Suche nach **Remko HTTP**.
4. Gib lediglich die **IP-Adresse** deiner Wärmepumpe ein (z. B. `192.168.1.50`).
5. Lege optional das Abfrageintervall fest (Standard: 30 Sekunden).

*Hinweis: Felder für Benutzername und Passwort werden nicht angezeigt und müssen nicht ausgefüllt werden.*

### YAML-Alternative

```yaml
remko_http:
  - host: "192.168.1.50"
    scan_interval: 30
    # Keine username/password Felder nötig
```

## 📄 Lizenz

Dieses Projekt steht unter der **MIT**-Lizenz. Siehe [LICENSE](LICENSE) für Details.

---

*Hinweis: Dieses Projekt ist nicht offiziell mit Remko verbunden. Die Nutzung erfolgt auf eigene Gefahr.*
