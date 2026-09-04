# remko_http

[![GitHub Release](https://img.shields.io/github/v/release/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange)](https://www.hacs.xyz/)
[![Validate](https://github.com/fuchsi585/remko_http/actions/workflows/validate.yml/badge.svg)](https://github.com/fuchsi585/remko_http/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http/blob/main/LICENSE)

**[🇬🇧 English version](README.en.md)**

> **Eine schlanke Home Assistant Custom Integration für Remko Wärmepumpen (Firmware 4.25).**
> *Direkter Datenabruf über die lokale HTTP-Schnittstelle – ganz ohne MQTT-Broker und ohne Passwort.*

## 📖 Inhaltsverzeichnis

* [Über das Projekt](#-über-das-projekt)
* [Warum diese Integration?](#-warum-diese-integration)
* [Voraussetzungen](#-voraussetzungen)
* [Installation](#-installation)
* [Konfiguration](#-konfiguration)
* [Verfügbare Daten](#-verfügbare-daten)
* [Fehlerbehebung](#-fehlerbehebung)
* [Lizenz](#-lizenz)

## 🚀 Über das Projekt

**remko_http** liest Betriebsdaten deiner Remko Wärmepumpe direkt aus dem lokalen Netzwerk aus. Dazu wird die integrierte Web-Schnittstelle (CGI) der Firmware 4.25 verwendet.

Das Besondere: Diese Firmware-Version benötigt für den lokalen Datenabruf keine Authentifizierung. Dadurch ist die Integration ressourcenschonend und einfach einzurichten. Es werden weder Benutzername noch Passwort benötigt.

## ⚖️ Warum diese Integration?

| Feature               | **remko_http** (Dieses Projekt) | MQTT-Lösungen (ab FW 4.26+)                   |
| :-------------------- | :------------------------------ | :-------------------------------------------- |
| **Protokoll**         | HTTP (CGI)                      | MQTT                                          |
| **Firmware**          | **4.25** (und älter)            | 4.26, 4.27, 4.28+                             |
| **Authentifizierung** | **Nicht erforderlich** 🎉       | Benutzername & Passwort erforderlich          |
| **Zusatzsoftware**    | Keine (Direktverbindung)        | MQTT-Broker (z. B. Mosquitto) erforderlich    |

## 📋 Voraussetzungen

* Eine Remko Wärmepumpe mit **Firmware-Version 4.25**.
* Die Wärmepumpe muss sich im gleichen lokalen Netzwerk wie Home Assistant befinden.
* Die **IP-Adresse** der Wärmepumpe muss bekannt sein. Eine feste IP-Adresse oder DHCP-Reservierung wird empfohlen.
* Es werden **keine Zugangsdaten** benötigt.

## 📦 Installation

### Option A: HACS (empfohlen)

1. Öffne HACS in Home Assistant.
2. Gehe zu **Integrationen** → Menü **(⋮)** → **Benutzerdefinierte Repositories**.
3. Füge die URL dieses Repositories hinzu und wähle als Typ **Integration**.
4. Suche nach **Remko HTTP**, installiere die Integration und starte Home Assistant neu.

### Option B: Manuelle Installation

1. Lade den Ordner `custom_components/remko_http` herunter.
2. Kopiere ihn in dein Home-Assistant-Verzeichnis unter `config/custom_components/`.
3. Starte Home Assistant neu.

```bash
# Beispiel via SSH
cd /config/custom_components
git clone https://github.com/fuchsi585/remko_http.git
```

## ⚙️ Konfiguration

Die Einrichtung erfolgt vollständig über die Home-Assistant-Benutzeroberfläche:

1. Gehe zu **Einstellungen** → **Geräte & Dienste**.
2. Klicke auf **Integration hinzufügen**.
3. Suche nach **Remko HTTP**.
4. Gib die **IP-Adresse** deiner Wärmepumpe ein, z. B. `192.168.1.50`.
5. Lege optional das **Abfrageintervall** fest. Der Standardwert beträgt 30 Sekunden.

> **Hinweis:** Es werden keine Felder für Benutzername oder Passwort angezeigt, da keine Zugangsdaten erforderlich sind.

## 📊 Verfügbare Daten

Die Integration stellt verschiedene Betriebs- und Messwerte der Wärmepumpe in Home Assistant zur Verfügung.

Dazu gehören unter anderem:

* Betriebsstatus
* Temperaturen
* Betriebs- und Leistungsdaten
* Warmwasserinformationen
* Einstellungen und Regelparameter
* Weitere von der Wärmepumpe bereitgestellte Werte

Die tatsächlich verfügbaren Entitäten können abhängig von Firmware und Gerätekonfiguration variieren.

## 🔧 Fehlerbehebung

### Die Wärmepumpe wird nicht gefunden

Überprüfe zunächst:

* Ist die Wärmepumpe eingeschaltet und mit dem lokalen Netzwerk verbunden?
* Ist die angegebene IP-Adresse korrekt?
* Befinden sich Home Assistant und die Wärmepumpe im selben Netzwerk?
* Blockiert eine Firewall die HTTP-Verbindung?

Du kannst außerdem testen, ob die Wärmepumpe über ihre IP-Adresse im Browser erreichbar ist.

### Es werden keine Werte angezeigt

Stelle sicher, dass die Wärmepumpe Firmware **4.25** verwendet und die lokale HTTP-Schnittstelle erreichbar ist.

Bei Problemen können die Home-Assistant-Logs weitere Informationen liefern.

## 📄 Lizenz

Dieses Projekt steht unter der **MIT-Lizenz**. Siehe [LICENSE](LICENSE) für weitere Informationen.

---

> **Hinweis:** Dieses Projekt ist nicht offiziell mit Remko verbunden. Die Nutzung erfolgt auf eigene Gefahr.

