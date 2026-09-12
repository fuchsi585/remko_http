# REMKO HTTP

[![GitHub Release](https://img.shields.io/github/v/release/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange)](https://www.hacs.xyz/)
[![Validate](https://github.com/fuchsi585/remko_http/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/fuchsi585/remko_http/actions/workflows/validate.yml)
[![Tests](https://github.com/fuchsi585/remko_http/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/fuchsi585/remko_http/actions/workflows/tests.yml)
[![License](https://img.shields.io/github/license/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http/blob/main/LICENSE)

Home Assistant custom integration for REMKO heat pumps using the local HTTP/CGI interface.

The integration communicates directly with the REMKO controller over the local network. No MQTT broker or cloud connection is required.

> 🇩🇪 Deutsch: [README.md](README.md)

## Features

- Local HTTP/CGI communication
- No cloud connection required
- No MQTT broker required
- Configuration through the Home Assistant UI
- Home Assistant Config Flow
- Operating and measurement data as Home Assistant entities
- Control of the domestic hot water target temperature and room climate mode
- Electrical energy calculation based on current power consumption
- HACS installation supported
- No username or password required on supported devices
- One heat pump per Home Assistant instance

## Supported Devices

| Device / Firmware | Status |
|---|---|
| REMKO WKF120 with firmware 4.25 | ✅ Tested |
| Other firmware versions | ❓ Untested |

The integration was developed and tested with a REMKO WKF120 using firmware 4.25.
Other firmware versions may use a different HTTP/CGI interface and are therefore not automatically compatible.
Feedback for additional models and firmware versions is welcome.

## Requirements

- Home Assistant 2024.1.0 or newer
- REMKO heat pump with supported firmware
- Network connectivity between Home Assistant and the heat pump
- Accessible local HTTP/CGI interface

A static IP address or DHCP reservation for the heat pump is recommended.

## Installation

### HACS

1. Open HACS in Home Assistant.
2. Go to **Integrations**.
3. Open **⋮ → Custom repositories**.
4. Add:

   `https://github.com/fuchsi585/remko_http`

5. Select **Integration** as repository type.
6. Install **REMKO HTTP**.
7. Restart Home Assistant.

### Manual

Copy the

`custom_components/remko_http`

directory to the Home Assistant configuration directory:

```text
/config/custom_components/remko_http/
```

Restart Home Assistant afterwards.

## Configuration

After installation:

1. Open **Settings → Devices & services**.
2. Select **Add Integration**.
3. Search for **REMKO HTTP**.
4. Enter the local IP address of the REMKO heat pump.
5. Select the polling interval and complete the configuration.

Example:

```text
192.168.1.50
```

Home Assistant will then communicate directly with the REMKO controller.

The polling interval can be set between 10 and 60 seconds. Its default value is
20 seconds. The IP address and polling interval can be changed later through the
integration options.

The integration currently supports exactly one heat pump per Home Assistant
instance.

## Communication

```text
Home Assistant
      │
      │ HTTP / CGI
      ▼
REMKO Heat Pump
```

The integration uses the local web/CGI interface provided by the REMKO controller.
No external server is required for communication.

> [!IMPORTANT]
> The CGI interface does not require authentication on supported devices. It
> should therefore only be reachable from a trusted local network and must not
> be exposed directly to the internet.

## Entities

| Type | Entities |
|---|---|
| Temperature | Domestic hot water target and current temperature, heating water target and current temperature, flow, return, circulation, outdoor, mixed outdoor and room temperature |
| State | Operating mode, domestic hot water request, circulation pump, fan and room climate mode |
| Power and energy | Electrical power, own consumption, thermal power, calculated electrical energy and device energy counter |
| Operation | Room humidity, pump speed, compressor starts and runtime |
| Control | Warmer/cooler offset, domestic hot water target temperature, room climate mode and one-time domestic hot water heating |

Diagnostic and helper entities such as device energy, own consumption and some
target values are disabled by default. They can be enabled through Home
Assistant's entity management when needed. The "Calculated energy" value is
maintained locally using the measured electrical power.

## Troubleshooting

### Heat pump not reachable

Check the following:

1. Is the heat pump powered on?
2. Is the heat pump reachable on the network?
3. Is the configured IP address correct?
4. Are Home Assistant and the heat pump on the same network?
5. Are firewall or VLAN rules blocking the connection?

### No data

If the connection is established but no values are available:

- Check the firmware version
- Check the IP address
- Check the HTTP/CGI interface
- Check the Home Assistant logs
- Include the model and firmware version when opening an issue

### Other firmware versions

The implementation is based on the HTTP/CGI communication observed on firmware 4.25.

Newer firmware versions may use a modified interface. Endpoints, data structures or query parameters may therefore differ.

## Technical Details

- Platform: Home Assistant
- Protocol: HTTP
- Interface: CGI
- Network: Local
- MQTT: Not required
- Cloud: Not required
- Tested firmware: 4.25

Communication takes place directly between Home Assistant and the REMKO controller.

## Development

[Issues](https://github.com/fuchsi585/remko_http/issues),
[discussions](https://github.com/fuchsi585/remko_http/discussions), and
[pull requests](https://github.com/fuchsi585/remko_http/pulls) are welcome.

## Acknowledgements

Special thanks to **Altrec** for the inspiration and groundwork surrounding the integration of REMKO heat pumps with Home Assistant. Many thanks also to the Home Assistant community for sharing knowledge and support.

## Disclaimer

This project is not affiliated with or officially supported by REMKO.

Use this integration at your own risk.

## License

[MIT License](LICENSE)

## Author

Developed by [fuchsi585](https://github.com/fuchsi585).
