# REMKO HTTP

[![GitHub Release](https://img.shields.io/github/v/release/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange)](https://www.hacs.xyz/)
[![Validate](https://github.com/fuchsi585/remko_http/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/fuchsi585/remko_http/actions/workflows/validate.yml)
[![Tests](https://github.com/fuchsi585/remko_http/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/fuchsi585/remko_http/actions/workflows/tests.yml)
[![License](https://img.shields.io/github/license/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http/blob/main/LICENSE)

Home Assistant Custom Integration für REMKO Wärmepumpen mit lokaler HTTP-/CGI-Schnittstelle.

Die Integration kommuniziert direkt mit der REMKO Steuerung über das lokale Netzwerk. Es wird weder ein MQTT-Broker noch eine Cloud-Verbindung benötigt.

> 🇬🇧 English: [README.en.md](README.en.md)

## Funktionen

- Lokale Kommunikation über HTTP/CGI
- Keine Cloud-Verbindung erforderlich
- Kein MQTT-Broker erforderlich
- Einrichtung über die Home-Assistant-Oberfläche
- Unterstützung von Home Assistant Config Flow
- Betriebs- und Messwerte als Home-Assistant-Entitäten
- Steuerung von Warmwasser-Solltemperatur und Raumklimamodus
- Berechnung des elektrischen Energieverbrauchs aus der aktuellen Leistung
- HACS-Installation möglich
- Kommunikation ohne Benutzername und Passwort bei unterstützten Geräten
- Eine Wärmepumpe pro Home-Assistant-Instanz

## Unterstützte Geräte

| Gerät / Firmware | Status |
|---|---|
| REMKO WKF120 mit Firmware 4.25 | ✅ Getestet |
| Andere Firmware-Versionen | ❓ Ungetestet |

Die Integration wurde mit einer REMKO WKF120 auf Basis von Firmware 4.25 entwickelt und getestet.
Andere Firmware-Versionen können eine abweichende HTTP-/CGI-Schnittstelle verwenden und sind daher nicht automatisch kompatibel.
Feedback zu weiteren Modellen und Firmware-Versionen ist willkommen.

## Voraussetzungen

- Home Assistant 2024.1.0 oder neuer, ältere Versionen werden nicht getestet.
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
5. Das Abfrageintervall festlegen und die Konfiguration abschließen.

Beispiel:

```text
192.168.1.50
```

Die Verbindung erfolgt anschließend direkt von Home Assistant zur REMKO Steuerung.

Das Abfrageintervall kann zwischen 10 und 60 Sekunden eingestellt werden. Der
Standardwert beträgt 20 Sekunden. IP-Adresse und Abfrageintervall lassen sich
später über die Optionen der Integration ändern.

Die Integration unterstützt derzeit genau eine Wärmepumpe pro
Home-Assistant-Instanz.

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

> [!IMPORTANT]
> Die CGI-Schnittstelle benötigt bei unterstützten Geräten keine Anmeldung. Sie
> sollte daher nur aus einem vertrauenswürdigen lokalen Netzwerk erreichbar sein
> und nicht direkt ins Internet freigegeben werden.

## Entitäten

Die folgende Tabelle enthält alle aktuell von der Sensorplattform bereitgestellten Entitäten. Die REMKO-ID bezeichnet den Parameter der lokalen HTTP-/CGI-Schnittstelle.

| Anzeigename | Interner Key | REMKO-ID | Einheit / Werteart | Beschreibung |
|---|---|---:|---|---|
| Kälter / Wärmer | `cold_hotter_state` | `1946` | K | Aktuelle Sollwertverschiebung für wärmer oder kälter. |
| Raumklima-Modus | `room_climate_mode` | `1088` | - | Gewählter Raumklimamodus: Automatik, Heizen, Standby oder Kühlen. |
| Aktuelle Betriebsart | `operating_status` | `5001` | - | Aktuelle übergeordnete Betriebsart der Anlage. |
| Wassertank Solltemperatur | `water_temp_req` | `1082` | °C | Eingestellte Solltemperatur des Warmwasserspeichers. |
| WW: Speicher Soll-Temp. | `hot_water_target_temperature` | `5038` | °C | Aktuell von der Regelung vorgegebene Solltemperatur des Warmwasserspeichers. |
| Wassertank Isttemperatur | `water_temp` | `5039` | °C | Gemessene Isttemperatur des Warmwasserspeichers. |
| Warmwasseranforderung | `hot_water_req_state` | `5064` | - | Zeigt an, ob eine Warmwasseranforderung aktiv ist oder sich im Standby befindet. |
| WW: Umschaltventil | `hot_water_diverter_valve` | `5162` | An/Aus | Ein-/Aus-Zustand der Komponente. |
| WW: Energie | `hot_water_energy` | `5376` | kWh | Für die Warmwasserbereitung erfasste thermische Energie. |
| WW: Hygienefunktion | `hot_water_hygiene_function` | `5803` | - | Zeigt an, ob die Warmwasser-Hygienefunktion aktiv ist oder sich im Standby befindet. |
| WW: Anforderung Zirkulation | `hot_water_circulation_demand` | `5133` | - | Status der Zirkulationsanforderung: Standby, aktiv oder gesperrt. |
| WW: Zirk. Soll-Temp. | `hot_water_circulation_target_temperature` | `5041` | °C | Solltemperatur der Warmwasserzirkulation. |
| WW: Zirkulationstemperatur | `circulation_temp` | `5027` | °C | Gemessene Temperatur der Warmwasserzirkulation. |
| WW: Zirkulationspumpe | `circulation_pump_state` | `5151` | An/Aus | Ein-/Aus-Zustand der Komponente. |
| Hydraulik: Anforderung | `hydraulics_demand` | `5040` | - | Von der Hydraulik angeforderter Betriebsmodus: Automatik, Heizen, Standby oder Kühlen. |
| Heizwasser Solltemperatur | `heating_req_temp` | `5085` | °C | Von der Regelung angeforderte Heizwassertemperatur. |
| Heizwasser Isttemperatur | `heating_actual_temp` | `5190` | °C | Gemessene Isttemperatur des Heizwassers. |
| Hydraulik: Leistung therm. | `hydraulics_thermal_power` | `5232` | W | Aktuelle thermische Leistung im Hydraulikkreis. |
| Hydraulik: Vorlauftemperatur (gemischt) | `mixed_flow_temp` | `5741` | °C | Gemessene Vorlauftemperatur des gemischten Heizkreises. |
| Hydraulik: Rücklauftemperatur (gemischt) | `mixed_return_temp` | `5476` | °C | Gemessene Rücklauftemperatur des gemischten Heizkreises. |
| Hydraulik: Soll-Volumenstrom | `hydraulics_target_flow_rate` | `5073` | l/min | Von der Regelung vorgegebener Volumenstrom. |
| Hydraulik: Ist-Volumenstrom | `hydraulics_actual_flow_rate` | `5582` | l/min | Gemessener Volumenstrom im Hydraulikkreis. |
| Hydraulik: Ist-Volumenstrom (gemischt) | `hydraulics_actual_flow_rate_mixed` | `5740` | l/min | Gemessener Volumenstrom im gemischten Heizkreis. |
| Hydraulik: Pumpendrehz. rel. | `hydraulics_pump_speed` | `5575` | % | Relative Drehzahl der Hydraulikpumpe. |
| Hydraulik: Energie Heizen | `hydraulics_heating_energy` | `5374` | kWh | Kumulierte thermische Energie für den Heizbetrieb. |
| Hydraulik: Energie Kühlen | `hydraulics_cooling_energy` | `5010` | kWh | Kumulierte thermische Energie für den Kühlbetrieb. |
| Hydraulik: Umschaltventil Kühlen | `hydraulics_cooling_diverter_valve` | `5166` | An/Aus | Ein-/Aus-Zustand der Komponente. |
| Außentemperatur | `out_temp` | `5032` | °C | Aktuell gemessene Außentemperatur. |
| Gemischte Außentemperatur | `mixed_temp` | `5055` | °C | Von der Regelung gebildete gemischte Außentemperatur. |
| Raum Solltemperatur | `room_temp_req` | `5075` | °C | Eingestellte Raum-Solltemperatur. |
| Raum Isttemperatur | `room_temp_act` | `5050` | °C | Aktuell gemessene Raumtemperatur. |
| Raumfeuchtigkeit | `room_humidity` | `5066` | % | Aktuell gemessene relative Luftfeuchtigkeit im Raum. |
| Pumpendrehzahl (Heizkreis) | `pump_speed` | `5576` | % | Relative Drehzahl der Heizkreispumpe. |
| HK ungemischt: Betriebsmodus | `heating_circuit_unmixed_operating_mode` | `5069` | - | Betriebsmodus des ungemischten Heizkreises: Automatik, Heizen, Standby oder Kühlen. |
| HK ungemischt: Soll-Temperatur | `heating_circuit_unmixed_target_temperature` | `5033` | °C | Solltemperatur des ungemischten Heizkreises. |
| HK ungemischt: Ist-Temperatur | `heating_circuit_unmixed_actual_temperature` | `5034` | °C | Gemessene Isttemperatur des ungemischten Heizkreises. |
| HK ungemischt: Taupunkt | `heating_circuit_unmixed_dew_point` | `5070` | °C | Berechneter Taupunkt für den ungemischten Heizkreis. |
| HK ungemischt: Status | `heating_circuit_unmixed_status` | `5710` | - | Regelungsstatus des ungemischten Heizkreises: Automatik, Komfort, Standby, Eco oder Schutzbetrieb. |
| HK ungemischt: Sollwertanpassung | `heating_circuit_unmixed_setpoint_adjustment` | `5717` | °C | Aktuelle Anpassung des Temperatursollwerts im ungemischten Heizkreis. |
| WP: Status | `heat_pump_status` | `5049` | - | Freigabe- und Sperrstatus der Wärmepumpe, etwa bereit, Vorlaufzeit, gesperrt oder deaktiviert. |
| WP: Betriebszustand | `heat_pump_sub_status` | `5473` | - | Detaillierter Betriebszustand der Wärmepumpe, etwa Heizen, Kühlen, Abtauen oder Alarm. |
| WP: Modus | `heat_pump_mode` | `5006` | - | Aktueller Modus der Wärmepumpe: Heizen oder Kühlen. |
| WP: Verbleibende Sperrzeit | `heat_pump_lockout_time` | `5572` | min | Noch verbleibende Sperrzeit der Wärmepumpe. |
| WP: Abtaustatus | `heat_pump_defrost_status` | `5626` | An/Aus | Ein-/Aus-Zustand der Komponente. |
| WP: Kompressorstatus | `heat_pump_compressor_status` | `5625` | An/Aus | Ein-/Aus-Zustand der Komponente. |
| WP: Fehlerstatus | `heat_pump_error_status` | `5002` | An/Aus | Ein-/Aus-Zustand der Komponente. |
| WP: Freigabesignal | `heat_pump_enable_signal` | `5004` | An/Aus | Ein-/Aus-Zustand der Komponente. |
| WP: Verdichtersperre | `heat_pump_compressor_lock` | `5005` | An/Aus | Ein-/Aus-Zustand der Komponente. |
| WP: Sperrsignal | `heat_pump_lock_signal` | `5174` | - | Zeigt an, ob das Sperrsignal die Wärmepumpe sperrt oder freigibt. |
| WP: Verdichterfrequenz | `heat_pump_compressor_frequency` | `5205` | Hz | Aktuelle Frequenz des Verdichters. |
| Lüfterstatus (außen) | `fan_state` | `5135` | An/Aus | Ein-/Aus-Zustand der Komponente. |
| WP: Heißgastemperatur | `heat_pump_hot_gas_temperature` | `5146` | °C | Gemessene Heißgastemperatur der Wärmepumpe. |
| Leistung | `power` | `5320` | W | Aktuelle elektrische Leistungsaufnahme der Wärmepumpe. |
| Thermische Leistung | `power_thermal` | `5321` | W | Aktuelle thermische Leistung der Wärmepumpe. |
| Kompressorstarts | `compressor_starts` | `5822` | – | Anzahl der Kompressorstarts. |
| WP: Laufzeit (Minuten) | `heat_pump_runtime_minutes` | `5823` | min | Laufzeit der Wärmepumpe in Minuten. |
| Laufzeit | `runtime_hours` | `5824` | h | Kumulierter Betriebsstundenzähler der Wärmepumpe. |
| WP: 4-Wege Ventil | `heat_pump_four_way_valve` | `5136` | An/Aus | Ein-/Aus-Zustand der Komponente. |
| Elektr. Energie (Stunde) | `energy_electrical_hour` | `5388` | kWh | Elektrischer Energieverbrauch für den angegebenen Zeitraum. |
| Elektr. Energie (Tag) | `energy_electrical_day` | `5293` | kWh | Elektrischer Energieverbrauch für den angegebenen Zeitraum. |
| Elektr. Energie (Woche) | `energy_electrical_week` | `5294` | kWh | Elektrischer Energieverbrauch für den angegebenen Zeitraum. |
| Elektr. Energie (Monat) | `energy_electrical_month` | `5295` | kWh | Elektrischer Energieverbrauch für den angegebenen Zeitraum. |
| Elektr. Energie (Jahr) | `energy_electrical_year` | `5296` | kWh | Elektrischer Energieverbrauch für den angegebenen Zeitraum. |
| Elektr. Energie (Stunde, temporär) | `energy_electrical_hour_temporary` | `5389` | kWh | Interner Stundenwert mit vier Nachkommastellen; als Diagnose markiert. |
| Elektr. Energie | `energy_electrical` | `5105` | kWh | Lokal aus der elektrischen Leistung berechneter Gesamtverbrauch; ID 5105 dient als Startwert. |
| Elektr. Energie (Gerät) | `energy_electrical_raw` | `5105` | kWh | Direkter, standardmäßig deaktivierter Energiezähler des REMKO-Geräts. |

Einzelne Sollwerte und Diagnosewerte können in Home Assistant standardmäßig deaktiviert sein.

### Berechnung der elektrischen Energie

Die Entität **Elektr. Energie** (`energy_electrical`) ist ein von der Integration
berechneter Gesamtzähler. REMKO stellt mit ID `5105` zwar einen eigenen
Energiezähler bereit, dieser ist für die kontinuierliche Verwendung jedoch nicht
immer zuverlässig. Deshalb verwendet die Integration ID `5105` vor allem als
Start- beziehungsweise Referenzwert und berechnet den weiteren Verbrauch aus der
aktuellen elektrischen Leistung der Wärmepumpe, ID `5320`.

Zwischen zwei erfolgreichen Abfragen wird die Energie mit der Trapezregel
berechnet:

```text
zusätzliche Energie [kWh]
  = (vorherige Leistung [W] + aktuelle Leistung [W]) / 2
    × Zeitdifferenz [h] / 1000
```

Durch die Mittelung der vorherigen und aktuellen Leistung werden Änderungen
zwischen zwei Abfragen besser berücksichtigt als bei der ausschließlichen
Verwendung eines einzelnen Messpunkts. Fehlt ein Leistungswert, bleibt der
bisherige Energiezähler erhalten. Bei einer Datenlücke, die größer als das
Vierfache des eingestellten Abfrageintervalls ist, wird für diesen Zeitraum keine
Energie hinzugerechnet, um unrealistische Sprünge zu vermeiden.

Der berechnete Wert wird lokal in Home Assistant gespeichert: der erste
gültige Wert sofort, weitere Änderungen regelmäßig im Abstand von zehn Minuten
und beim Beenden der Integration. Nach einem Neustart wird der gespeicherte Wert
weitergeführt. Ist noch kein gültiger Speicherwert vorhanden, dient der direkte
REMKO-Zähler `5105` als Ausgangswert. Dieser bleibt separat als standardmäßig
deaktivierte Diagnose-Entität **Elektr. Energie (Gerät)**
(`energy_electrical_raw`) verfügbar.

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

[Issues](https://github.com/fuchsi585/remko_http/issues),
[Diskussionen](https://github.com/fuchsi585/remko_http/discussions) und
[Pull Requests](https://github.com/fuchsi585/remko_http/pulls) sind willkommen.

## Danksagung

Vielen Dank an **Altrec** für die Inspiration und die Vorarbeit rund um die Integration von REMKO Wärmepumpen in Home Assistant. Ebenso vielen Dank an die Home-Assistant-Community für den Austausch und die zahlreichen Erkenntnisse.

## Haftungsausschluss

Dieses Projekt ist nicht offiziell mit REMKO verbunden und wird nicht von REMKO unterstützt.

Die Verwendung erfolgt auf eigene Verantwortung.

## Lizenz

[MIT License](LICENSE)

## Autor

Entwickelt von [fuchsi585](https://github.com/fuchsi585).
