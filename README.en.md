# remko_http

[![GitHub Release](https://img.shields.io/github/v/release/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange)](https://www.hacs.xyz/)
[![Validate](https://github.com/fuchsi585/remko_http/actions/workflows/validate.yml/badge.svg)](https://github.com/fuchsi585/remko_http/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http/blob/main/LICENSE)

**[🇩🇪 Deutsche Version](README.md)**

> **A lightweight Home Assistant custom integration for Remko heat pumps (firmware 4.25).**
> *Direct data retrieval via the local HTTP interface – no MQTT broker and no password required.*

## 📖 Table of Contents

* [About the Project](#-about-the-project)
* [Why This Integration?](#-why-this-integration)
* [Requirements](#-requirements)
* [Installation](#-installation)
* [Configuration](#-configuration)
* [Available Data](#-available-data)
* [Troubleshooting](#-troubleshooting)
* [License](#-license)

## 🚀 About the Project

**remko_http** reads operating data from your Remko heat pump directly over the local network. It uses the built-in web interface (CGI) provided by firmware 4.25.

The key advantage is that this firmware version does not require authentication for local data access. This makes the integration lightweight and easy to set up. No username or password is required.

## ⚖️ Why This Integration?

| Feature                 | **remko_http** (This Project) | MQTT Solutions (FW 4.26+)                |
| :---------------------- | :---------------------------- | :--------------------------------------- |
| **Protocol**            | HTTP (CGI)                    | MQTT                                     |
| **Firmware**            | **4.25** (and earlier)        | 4.26, 4.27, 4.28+                        |
| **Authentication**      | **Not required** 🎉           | Username & password required             |
| **Additional software** | None (direct connection)      | MQTT broker (e.g. Mosquitto) required    |

## 📋 Requirements

* A Remko heat pump running **firmware version 4.25**.
* The heat pump must be connected to the same local network as Home Assistant.
* The heat pump's **IP address** must be known. A static IP address or DHCP reservation is recommended.
* **No credentials** are required.

## 📦 Installation

### Option A: HACS (Recommended)

1. Open HACS in Home Assistant.
2. Go to **Integrations** → **(⋮) Menu** → **Custom repositories**.
3. Add the URL of this repository and select **Integration** as the type.
4. Search for **Remko HTTP**, install the integration, and restart Home Assistant.

### Option B: Manual Installation

1. Download the `custom_components/remko_http` folder.
2. Copy it to your Home Assistant configuration directory under `config/custom_components/`.
3. Restart Home Assistant.

```bash
# Example via SSH
cd /config/custom_components
git clone https://github.com/fuchsi585/remko_http.git
```

## ⚙️ Configuration

The integration can be configured entirely through the Home Assistant user interface:

1. Go to **Settings** → **Devices & services**.
2. Click **Add Integration**.
3. Search for **Remko HTTP**.
4. Enter the **IP address** of your heat pump, for example `192.168.1.50`.
5. Optionally configure the **polling interval**. The default is 30 seconds.

> **Note:** No username or password fields are displayed because no credentials are required.

## 📊 Available Data

The integration provides various operating and measurement values from the heat pump in Home Assistant.

These include, among others:

* Operating status
* Temperatures
* Operating and power data
* Domestic hot water information
* Settings and control parameters
* Other values provided by the heat pump

The exact entities available may vary depending on the firmware version and device configuration.

## 🔧 Troubleshooting

### The heat pump cannot be found

Check the following:

* Is the heat pump powered on and connected to the local network?
* Is the configured IP address correct?
* Are Home Assistant and the heat pump connected to the same network?
* Is a firewall blocking the HTTP connection?

You can also check whether the heat pump's web interface is accessible through its IP address using a browser.

### No values are displayed

Make sure the heat pump is running **firmware 4.25** and that its local HTTP interface is accessible.

If problems persist, check the Home Assistant logs for additional information.

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

> **Note:** This project is not officially affiliated with Remko. Use at your own risk.

