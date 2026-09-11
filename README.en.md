# REMKO HTTP

[![GitHub License](https://img.shields.io/github/license/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http)
[![GitHub Release](https://img.shields.io/github/v/release/fuchsi585/remko_http)](https://github.com/fuchsi585/remko_http)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)

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
- HACS installation supported
- No username or password required on supported devices

## Supported Devices

| Device / Firmware | Status |
|---|---|
| REMKO heat pump with firmware 4.25 | ✅ Tested |
| Other firmware versions | ❓ Untested |

The integration was developed and tested with REMKO systems using firmware 4.25.
Other firmware versions may use a different HTTP/CGI interface and are therefore not automatically compatible.
Feedback for additional models and firmware versions is welcome.

## Requirements

- Home Assistant
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
5. Complete the configuration.

Example:

```text
192.168.1.50
```

Home Assistant will then communicate directly with the REMKO controller.

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

## Entities

- Temperatures
- Operating states
- Domestic hot water values
- Power values
- Operating parameters
- Additional values exposed by the controller

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

Pull requests and issues are welcome.

## Acknowledgements

Special thanks to **Altrec** for the inspiration and groundwork surrounding the integration of REMKO heat pumps with Home Assistant. Many thanks also to the Home Assistant community for sharing knowledge and insights.

## Disclaimer

This project is not affiliated with or officially supported by REMKO.

Use this integration at your own risk.

## License

MIT License

## Author

Developed by [fuchsi585](https://github.com/fuchsi585).