# REMKO Home Assistant Integration – HTTP

[![GitHub](https://img.shields.io/github/license/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http)
[![GitHub release](https://img.shields.io/github/v/release/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)

**A Home Assistant custom integration for REMKO heat pumps using the local HTTP/CGI interface.**

`remko_http` connects compatible **REMKO heat pumps to Home Assistant** using the local network and the heat pump's built-in **HTTP/CGI interface**.
No MQTT broker, cloud connection, username or password is required.

> 🇩🇪 Deutsche Dokumentation: [README.md](README.md)

---

## ⭐ Why use this integration?

Do you want to connect your **REMKO heat pump to Home Assistant** without using an additional MQTT broker or cloud service?
`remko_http` provides a simple local integration for compatible REMKO systems that expose their data through the local HTTP/CGI interface.

### Key features

- 🏠 **Home Assistant integration** for REMKO heat pumps
- 🌐 **Local communication** over your own network
- 🔌 Uses the REMKO **HTTP/CGI interface**
- 🚫 **No MQTT broker required**
- 🚫 **No cloud connection required**
- 🔑 **No username or password required**
- ⚡ Easy configuration through the Home Assistant UI
- 🧩 **HACS installation** supported
- 📊 Heat pump data available directly in Home Assistant

---

## ⚠️ Compatibility

This integration was developed and tested for **REMKO heat pumps using firmware 4.25** that provide the required local HTTP/CGI interface.

| Requirement | Support |
|---|---|
| Home Assistant | ✅ |
| REMKO heat pump | ✅ |
| Firmware 4.25 | ✅ |
| Local HTTP/CGI interface | ✅ |
| HACS | ✅ |
| MQTT | ❌ not required |
| Cloud connection | ❌ not required |
| Username / password | ❌ not required |

### Firmware versions

Compatibility depends on the firmware installed on the REMKO controller.

**Firmware 4.25 and compatible systems:**

- local HTTP/CGI communication
- no authentication required
- direct communication with Home Assistant

**Newer firmware versions may use a different communication interface.**

In particular, systems running **firmware 4.26 or newer** may behave differently. Please check the firmware version of your REMKO system before installing this integration.

> If you are using a different firmware version and the integration works — or does not work — please consider opening an issue with your heat pump model and firmware version.

---

## 🚀 Installation

### Option 1 – HACS

The easiest way to install `remko_http` is through [HACS](https://hacs.xyz/).

1. Open **HACS** in Home Assistant.
2. Go to **Integrations**.
3. Open the **⋮** menu in the top-right corner.
4. Select **Custom repositories**.
5. Add:

   `https://github.com/fuchsi585/remko_http`

6. Select **Integration** as the repository type.
7. Search for **REMKO HTTP**.
8. Install the integration.
9. Restart Home Assistant.

After restarting Home Assistant, go to:

**Settings → Devices & services → Add Integration**

and search for:

**REMKO HTTP**

---

### Option 2 – Manual installation

Download or clone this repository and copy the directory
`custom_components/remko_http`
to your Home Assistant configuration directory:
```text
/config/custom_components/remko_http/
```
The resulting structure should look similar to:
```text
/config
└── custom_components
    └── remko_http
```

Restart Home Assistant after installing the integration.

---

### Installation via SSH

If you have SSH access to your Home Assistant configuration directory:
```bash
cd /config/custom_components
git clone https://github.com/fuchsi585/remko_http.git
```
Then restart Home Assistant.

---

## ⚙️ Configuration

After installation:
1. Open **Settings → Devices & services**.
2. Select **Add Integration**.
3. Search for **REMKO HTTP**.
4. Enter the local IP address of your REMKO heat pump.
5. Confirm the configuration.

Example:
```text
192.168.1.50
```

Home Assistant will then communicate directly with the REMKO heat pump over your local network.

### Recommended: static IP address

For reliable operation, it is recommended to assign your REMKO heat pump either:
- a static IP address, or
- a DHCP reservation in your router.
This prevents the heat pump's IP address from changing.

---

## 🌐 How does it work?

`remko_http` communicates directly with the local web/CGI interface provided by compatible REMKO controllers.
The basic architecture looks like this:
```text
┌─────────────────────┐
│    Home Assistant   │
└──────────┬──────────┘
           │
           │ HTTP / CGI
           │
           ▼
┌─────────────────────┐
│   REMKO Heat Pump   │
│                     │
│  Local network      │
│  HTTP/CGI interface │
└─────────────────────┘
```

No external server is required.
This means:

- Home Assistant → REMKO
- direct communication over the local network
- no MQTT broker
- no REMKO cloud connection
- no additional gateway software
---

## 📊 Available data

The integration exposes data provided by the REMKO controller as Home Assistant entities.
Depending on the heat pump model and firmware, this can include:
- 🌡️ Temperature values
- 🔥 Operating states
- 💧 Domestic hot water information
- ⚡ Operating and power data
- ⚙️ Configuration and control parameters
- 📈 Additional values provided by the controller
The exact entities available depend on the **REMKO model, firmware version and system configuration**.

---

## 🏠 Using the integration in Home Assistant

After successful setup, the REMKO heat pump is added as a device in Home Assistant.
The available sensors can be used for:

- Home Assistant dashboards
- energy monitoring
- heating automations
- temperature monitoring
- notifications
- statistics
- custom automations

Example:
```text
REMKO Heat Pump
├── Operating status
├── Outdoor temperature
├── Flow temperature
├── Domestic hot water
├── Power / operating data
└── Additional measurements
```

The exact entities depend on the connected REMKO system.

---

## 🔧 Troubleshooting

### The REMKO heat pump cannot be found

Check the following:
1. Is the heat pump powered on?
2. Is it connected to the local network?
3. Is the configured IP address correct?
4. Are Home Assistant and the heat pump on the same network?
5. Is a firewall blocking the connection?

First, try opening the heat pump's IP address in a web browser.
For example:

```text
http://192.168.1.50/
```
---

### No data is available

Check:
- REMKO firmware version
- IP address
- network connection
- accessibility of the local HTTP interface
- Home Assistant logs

The integration requires a REMKO controller that provides the expected **HTTP/CGI interface**.

---

### My firmware is newer than 4.25

Newer REMKO firmware may use a different communication interface.
If your system is running **firmware 4.26, 4.27 or newer**, this integration may not work.
There are other approaches in the Home Assistant community for newer REMKO systems, including MQTT- and SmartWeb-based solutions.
If you have successfully tested `remko_http` with a newer firmware version, please open an issue and share the relevant details.

---

## 🐛 Reporting a problem

If the integration does not work correctly, please create a [GitHub Issue](https://github.com/fuchsi585/remko_http/issues).

Please **do not post passwords, tokens or other sensitive information** in GitHub issues.

---

## 💡 Feature requests

Have an idea for a new feature or would you like additional REMKO data to be available in Home Assistant?
Feel free to open a feature request.

---

## 🔒 Privacy

`remko_http` is designed for **local communication** between Home Assistant and the REMKO heat pump.
No external cloud connection is required.
Communication takes place within your local network.
---

## ⚡ HTTP or MQTT?

There are several ways to integrate REMKO heat pumps with Home Assistant.
`remko_http` intentionally focuses on a simple local HTTP/CGI-based approach.
| | `remko_http` | MQTT-based solutions |
|---|---|---|
| Communication | HTTP / CGI | MQTT |
| Local communication | ✅ | ✅ |
| MQTT broker | ❌ | ✅ |
| Cloud required | ❌ | Depends on solution |
| Username/password | ❌ for supported firmware | Depends on system |
| Additional software | ❌ | Usually required |
| Main focus | Compatible HTTP firmware | Systems using MQTT |

**If your REMKO heat pump provides the required local HTTP/CGI interface, `remko_http` provides a straightforward way to connect it directly to Home Assistant.**

---

## 📚 Background

REMKO heat pumps have been integrated with Home Assistant using several different approaches.
Depending on the REMKO model and firmware, users have explored communication methods including:
- HTTP / CGI
- MQTT
- SmartWeb
`remko_http` focuses specifically on the **local HTTP/CGI interface** available on compatible REMKO systems.

---

## ⭐ Support the project

If `remko_http` is useful to you, consider giving the repository a ⭐ **Star** on GitHub.
Stars help other REMKO and Home Assistant users discover the project.
👉 [GitHub Repository](https://github.com/fuchsi585/remko_http)

---

## 📄 License

This project is licensed under the **MIT License**.
See [LICENSE](LICENSE) for details.

---

## ⚠️ Disclaimer

This project is **not affiliated with or officially supported by REMKO**.
REMKO is a trademark of its respective owner.
Use this integration at your own risk.

---

## 👤 Author

Developed by [fuchsi585](https://github.com/fuchsi585).
Issues, pull requests, feedback and improvements are welcome.
