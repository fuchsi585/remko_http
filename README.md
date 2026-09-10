# REMKO Home Assistant Integration – HTTP

[![GitHub](https://img.shields.io/github/license/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http)
[![GitHub release](https://img.shields.io/github/v/release/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)

**Home Assistant Custom Integration für REMKO Wärmepumpen mit lokaler HTTP-/CGI-Schnittstelle.**

`remko_http` ermöglicht die lokale Integration kompatibler **REMKO Wärmepumpen in Home Assistant**. Die Kommunikation erfolgt direkt über das lokale Netzwerk per **HTTP/CGI** – ohne Cloud, ohne MQTT-Broker und ohne Benutzername oder Passwort.

> 🇬🇧 English documentation: [README.en.md](README.en.md)

---

## ⭐ Warum diese Integration?

Du möchtest deine **REMKO Wärmepumpe mit Home Assistant verbinden**, möchtest aber keinen zusätzlichen MQTT-Broker verwenden?

Diese Integration wurde speziell für REMKO-Systeme entwickelt, deren Firmware die lokale HTTP-/CGI-Schnittstelle bereitstellt.

### Die wichtigsten Vorteile

- 🏠 **Home Assistant Integration** für REMKO Wärmepumpen
- 🌐 **Lokale Kommunikation** innerhalb des eigenen Netzwerks
- 🔌 Kommunikation über **HTTP/CGI**
- 🚫 **Kein MQTT-Broker erforderlich**
- 🚫 **Keine Cloud-Verbindung erforderlich**
- 🔑 **Keine Benutzer- oder Passwortdaten erforderlich**
- ⚡ Einfaches Setup direkt über die Home-Assistant-Oberfläche
- 🧩 Installation über **HACS** möglich
- 📊 Betriebs- und Messwerte direkt in Home Assistant verfügbar

---

## ⚠️ Kompatibilität

Diese Integration wurde für **REMKO Wärmepumpen mit Firmware 4.25** entwickelt, die die lokale HTTP-/CGI-Schnittstelle bereitstellen.

| Voraussetzung | Unterstützung |
|---|---|
| Home Assistant | ✅ |
| REMKO Wärmepumpe | ✅ |
| Firmware 4.25 | ✅ |
| Lokale HTTP-/CGI-Schnittstelle | ✅ |
| HACS | ✅ |
| MQTT | ❌ nicht erforderlich |
| Cloud-Verbindung | ❌ nicht erforderlich |
| Benutzername / Passwort | ❌ nicht erforderlich |

### Firmware-Versionen

Die Unterstützung hängt von der Firmware der REMKO-Steuerung ab.

**Firmware 4.25 und kompatible Systeme:**

- lokale HTTP-/CGI-Kommunikation
- keine Authentifizierung erforderlich
- direkte Kommunikation mit Home Assistant

**Neuere Firmware-Versionen können eine andere Kommunikationsschnittstelle verwenden.**

Insbesondere bei Firmware-Versionen ab **4.26** kann sich das Kommunikationsverhalten unterscheiden. Bitte prüfe daher vor der Installation die Firmware deiner Wärmepumpe.

> Wenn du eine andere Firmware verwendest und die Integration nicht funktioniert, kannst du gerne ein Issue mit Modell und Firmware-Version eröffnen.

---

## 🚀 Installation

### Option 1 – HACS

Die Installation über [HACS](https://hacs.xyz/) ist die einfachste Variante.

1. Öffne **HACS** in Home Assistant.
2. Öffne **Integrationen**.
3. Klicke oben rechts auf das Menü **⋮**.
4. Wähle **Benutzerdefinierte Repositories**.
5. Füge dieses Repository hinzu:

   `https://github.com/fuchsi585/remko_http`

6. Wähle als Repository-Typ **Integration**.
7. Suche anschließend nach **REMKO HTTP**.
8. Installiere die Integration.
9. Starte Home Assistant neu.

Nach dem Neustart steht die Integration unter:
**Einstellungen → Geräte & Dienste → Integration hinzufügen**
zur Verfügung.

---

### Option 2 – Manuelle Installation

Lade das Repository herunter und kopiere den Ordner
`custom_components/remko_http`
in dein Home-Assistant-Konfigurationsverzeichnis:

```text
/config/custom_components/remko_http/
```
Die Verzeichnisstruktur sollte anschließend so aussehen:
```text
/config
└── custom_components
    └── remko_http
```
Anschließend Home Assistant neu starten.

---

### Installation über SSH

Wenn du Zugriff auf das Home-Assistant-Dateisystem über SSH hast:
```bash
cd /config/custom_components
git clone https://github.com/fuchsi585/remko_http.git
```
Danach Home Assistant neu starten.

---

## ⚙️ Einrichtung

Nach der Installation:
1. Öffne **Einstellungen → Geräte & Dienste**.
2. Klicke auf **Integration hinzufügen**.
3. Suche nach **REMKO HTTP**.
4. Gib die lokale IP-Adresse deiner REMKO Wärmepumpe ein.
5. Bestätige die Einrichtung.
6. Home Assistant verbindet sich anschließend direkt mit der Wärmepumpe.

Beispiel:
```text
192.168.1.50
```

### Empfohlen: feste IP-Adresse

Damit Home Assistant die Wärmepumpe zuverlässig erreicht, solltest du für die REMKO Wärmepumpe eine **feste IP-Adresse oder DHCP-Reservierung** verwenden.

---

## 🌐 Wie funktioniert die Kommunikation?

Die Integration kommuniziert direkt mit der lokalen Web-/CGI-Schnittstelle der REMKO-Steuerung.
Vereinfacht sieht die Verbindung so aus:
```text
┌─────────────────────┐
│    Home Assistant   │
└──────────┬──────────┘
           │
           │ HTTP / CGI
           │
           ▼
┌─────────────────────┐
│   REMKO Wärmepumpe  │
│                     │
│  lokale Netzwerk-   │
│  schnittstelle      │
└─────────────────────┘
```

Es ist **keine Kommunikation über einen externen Server erforderlich**.
Das bedeutet:
- Home Assistant → REMKO
- direkt im lokalen Netzwerk
- kein MQTT-Broker
- keine REMKO-Cloud
- keine zusätzliche Gateway-Software

---

## 📊 Verfügbare Daten

Die Integration stellt von der REMKO Wärmepumpe bereitgestellte Betriebs- und Messwerte in Home Assistant zur Verfügung.
Je nach Modell und Firmware können unter anderem folgende Informationen verfügbar sein:

- 🌡️ Temperaturen
- 🔥 Betriebszustände
- 💧 Warmwasserinformationen
- ⚡ Betriebs- und Leistungsdaten
- ⚙️ Einstellungen und Regelparameter
- 📈 weitere von der Steuerung bereitgestellte Werte

Die tatsächlich verfügbaren Entitäten können abhängig von **Wärmepumpenmodell, Firmware und Gerätekonfiguration** variieren.

---

## 🏠 Verwendung in Home Assistant

Nach erfolgreicher Einrichtung wird die REMKO Wärmepumpe als Gerät in Home Assistant angelegt.
Die bereitgestellten Sensoren können anschließend beispielsweise verwendet werden für:
- Home-Assistant-Dashboards
- Energieüberwachung
- Heizungsautomatisierungen
- Temperaturüberwachung
- Benachrichtigungen
- Statistiken
- eigene Automationen

Beispiel:
```text
REMKO Wärmepumpe
├── Betriebsstatus
├── Außentemperatur
├── Vorlauftemperatur
├── Warmwasser
├── Leistungsdaten
└── weitere Messwerte
```
Die genaue Liste hängt vom jeweiligen REMKO-System ab.

---

## 🔧 Fehlerbehebung

### Die REMKO Wärmepumpe wird nicht gefunden

Überprüfe zunächst:
1. Ist die Wärmepumpe eingeschaltet?
2. Ist sie mit dem lokalen Netzwerk verbunden?
3. Ist die angegebene IP-Adresse korrekt?
4. Befinden sich Home Assistant und die Wärmepumpe im gleichen Netzwerk?
5. Wird die Kommunikation eventuell durch eine Firewall blockiert?

Teste zunächst, ob die IP-Adresse der Wärmepumpe im Browser erreichbar ist.
Beispiel:

```text
http://192.168.1.50/
```

---

### Es werden keine Werte angezeigt

Überprüfe:
- Firmware-Version der REMKO Wärmepumpe
- IP-Adresse
- Netzwerkverbindung
- Erreichbarkeit der lokalen HTTP-Schnittstelle
- Home-Assistant-Logs
Diese Integration benötigt eine REMKO Steuerung, die die erwartete **HTTP-/CGI-Schnittstelle** bereitstellt.

---

### Meine Firmware ist neuer als 4.25

Neuere REMKO-Firmware kann eine andere Kommunikationsschnittstelle verwenden.
Wenn deine Wärmepumpe beispielsweise Firmware **4.26, 4.27 oder neuer** verwendet, kann diese Integration möglicherweise nicht funktionieren.
In der Home-Assistant-Community gibt es für neuere REMKO-Systeme auch Ansätze auf Basis von MQTT bzw. SmartWeb.
Wenn du eine andere Firmware erfolgreich mit dieser Integration verwendest, freuen wir uns über einen Erfahrungsbericht.

---

## 🐛 Fehler melden

Wenn die Integration bei dir nicht funktioniert, erstelle bitte ein [GitHub Issue](https://github.com/fuchsi585/remko_http/issues).

Bitte **keine Passwörter, Tokens oder andere persönliche Zugangsdaten** in Issues veröffentlichen.

---

## 💡 Feature Requests

Du hast eine Idee für eine zusätzliche Funktion oder möchtest weitere Daten deiner REMKO Wärmepumpe in Home Assistant verfügbar machen?
Dann kannst du gerne ein Feature Request als GitHub Issue erstellen.

---

## 🔒 Datenschutz

Diese Integration ist für eine **lokale Kommunikation** zwischen Home Assistant und der REMKO Wärmepumpe konzipiert.
Es ist keine externe Cloud-Verbindung erforderlich.
Die Kommunikation findet grundsätzlich innerhalb deines lokalen Netzwerks statt.

---

## ⚡ MQTT oder HTTP?

Es gibt verschiedene Möglichkeiten, REMKO Wärmepumpen in Home Assistant einzubinden.
`remko_http` verfolgt bewusst einen möglichst einfachen lokalen Ansatz:
| | remko_http | MQTT-basierte Lösungen |
|---|---|---|
| Kommunikation | HTTP / CGI | MQTT |
| Lokal | ✅ | ✅ |
| MQTT-Broker | ❌ | ✅ |
| Cloud notwendig | ❌ | je nach Lösung |
| Benutzername/Passwort | ❌ bei unterstützter Firmware | abhängig von System |
| Einrichtung | einfach | abhängig von MQTT-Setup |
| Schwerpunkt | ältere/kompatible HTTP-Firmware | neuere Systeme |

**Wenn deine REMKO Wärmepumpe die benötigte lokale HTTP-/CGI-Schnittstelle bereitstellt, ist `remko_http` eine einfache Möglichkeit, sie direkt in Home Assistant einzubinden.**

---

## 📚 Hintergrund

Die lokale Kommunikation mit REMKO Wärmepumpen wurde bereits von verschiedenen Home-Assistant-Nutzern untersucht und in der Home-Assistant-Community diskutiert.
Dabei gibt es unterschiedliche Ansätze für unterschiedliche REMKO Firmware-Versionen und Kommunikationswege, darunter HTTP/CGI, MQTT und SmartWeb.
Dieses Projekt konzentriert sich auf die **lokale HTTP-/CGI-Kommunikation** kompatibler REMKO Systeme.

---

## ⭐ Unterstütze das Projekt

Wenn dir diese Integration hilft, kannst du das Projekt auf GitHub mit einem ⭐ **Star** unterstützen.
Das hilft anderen REMKO- und Home-Assistant-Nutzern dabei, das Projekt zu finden.
👉 [GitHub Repository](https://github.com/fuchsi585/remko_http)

---

## 📄 Lizenz

Dieses Projekt steht unter der **MIT License**.
Siehe [LICENSE](LICENSE) für weitere Informationen.

---

## ⚠️ Haftungsausschluss

Dieses Projekt ist **nicht offiziell mit REMKO verbunden**.
REMKO ist eine Marke der jeweiligen Rechteinhaber.
Die Verwendung dieser Integration erfolgt auf eigene Verantwortung.

---

## 👤 Autor

Entwickelt von [fuchsi585](https://github.com/fuchsi585).
Pull Requests, Issues, Erfahrungsberichte und Verbesserungsvorschläge sind willkommen.
