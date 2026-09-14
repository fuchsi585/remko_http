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

The following table lists every entity currently provided by the sensor platform. The REMKO ID identifies the parameter used by the local HTTP/CGI interface.

| Display name | Internal key | REMKO ID | Unit / value type | Description |
|---|---|---:|---|---|
| Warmer / cooler | `cold_hotter_state` | `1946` | K | Current warmer/cooler setpoint offset. |
| Room climate mode | `room_climate_mode` | `1088` | - | Selected room climate mode: automatic, heating, standby, or cooling. |
| Current operating mode | `operating_status` | `5001` | - | Current overall operating mode of the system. |
| Hot water target temperature | `water_temp_req` | `1082` | °C | Configured target temperature of the domestic hot water tank. |
| DHW: Tank target temp. | `hot_water_target_temperature` | `5038` | °C | Current domestic hot water tank target temperature requested by the controller. |
| Hot water temperature | `water_temp` | `5039` | °C | Measured temperature of the domestic hot water tank. |
| Hot water request | `hot_water_req_state` | `5064` | - | Indicates whether a domestic hot water request is active or on standby. |
| DHW: Switch valve | `hot_water_diverter_valve` | `5162` | On/off | On/off state of the component. |
| DHW: Heating energy | `hot_water_energy` | `5376` | kWh | Thermal energy recorded for domestic hot water production. |
| DHW: hygiene function | `hot_water_hygiene_function` | `5803` | - | Indicates whether the domestic hot water hygiene function is active or on standby. |
| DHW: Circulation demand | `hot_water_circulation_demand` | `5133` | - | Circulation demand status: standby, active, or blocked. |
| DHW: Circulation target temp. | `hot_water_circulation_target_temperature` | `5041` | °C | Target temperature of the domestic hot water circulation system. |
| DHW: Circulation temperature | `circulation_temp` | `5027` | °C | Measured temperature of the domestic hot water circulation system. |
| DHW: Circulation pump | `circulation_pump_state` | `5151` | On/off | On/off state of the component. |
| Hydraulics: Requirement | `hydraulics_demand` | `5040` | - | Operating mode requested by the hydraulic system: automatic, heating, standby, or cooling. |
| Heating water target temperature | `heating_req_temp` | `5085` | °C | Heating water temperature requested by the controller. |
| Heating water temperature | `heating_actual_temp` | `5190` | °C | Measured heating water temperature. |
| Hydraulics: Thermal output | `hydraulics_thermal_power` | `5232` | W | Current thermal power in the hydraulic circuit. |
| Hydraulics: Mixed flow temperature | `mixed_flow_temp` | `5741` | °C | Measured flow temperature of the mixed heating circuit. |
| Hydraulics: Mixed return temperature | `mixed_return_temp` | `5476` | °C | Measured return temperature of the mixed heating circuit. |
| Hydraulics: Target volume flow | `hydraulics_target_flow_rate` | `5073` | l/min | Volume flow requested by the controller. |
| Hydraulics: Actual flow rate | `hydraulics_actual_flow_rate` | `5582` | l/min | Measured volume flow in the hydraulic circuit. |
| Hydraulics: Mixed actual flow rate | `hydraulics_actual_flow_rate_mixed` | `5740` | l/min | Measured volume flow in the mixed heating circuit. |
| Hydraulics: Pump speed rel. | `hydraulics_pump_speed` | `5575` | % | Relative speed of the hydraulic pump. |
| Hydraulics: Heating energy | `hydraulics_heating_energy` | `5374` | kWh | Cumulative thermal energy for heating operation. |
| Hydraulics: Cooling energy | `hydraulics_cooling_energy` | `5010` | kWh | Cumulative thermal energy for cooling operation. |
| Hydraulics: Switch valve cooling | `hydraulics_cooling_diverter_valve` | `5166` | On/off | On/off state of the component. |
| Outdoor temperature | `out_temp` | `5032` | °C | Current measured outdoor temperature. |
| Mixed outdoor temperature | `mixed_temp` | `5055` | °C | Mixed outdoor temperature calculated by the controller. |
| Room target temperature | `room_temp_req` | `5075` | °C | Configured room target temperature. |
| Room temperature | `room_temp_act` | `5050` | °C | Current measured room temperature. |
| Room humidity | `room_humidity` | `5066` | % | Current measured relative humidity in the room. |
| Pump speed (heating circuit) | `pump_speed` | `5576` | % | Relative speed of the heating circuit pump. |
| Unmixed HC: Operating mode | `heating_circuit_unmixed_operating_mode` | `5069` | - | Operating mode of the unmixed heating circuit: automatic, heating, standby, or cooling. |
| Unmixed HC: Target temperature | `heating_circuit_unmixed_target_temperature` | `5033` | °C | Target temperature of the unmixed heating circuit. |
| Unmixed HC: Actual temperature | `heating_circuit_unmixed_actual_temperature` | `5034` | °C | Measured temperature of the unmixed heating circuit. |
| Unmixed HC: Dew point | `heating_circuit_unmixed_dew_point` | `5070` | °C | Calculated dew point for the unmixed heating circuit. |
| Unmixed HC: Status | `heating_circuit_unmixed_status` | `5710` | - | Control status of the unmixed heating circuit: automatic, comfort, standby, eco, or protection. |
| Unmixed HC: Setpoint adjustment | `heating_circuit_unmixed_setpoint_adjustment` | `5717` | °C | Current temperature setpoint adjustment for the unmixed heating circuit. |
| HP: Status | `heat_pump_status` | `5049` | - | Heat pump release and lock status, such as ready, lead time, blocked, or disabled. |
| HP: Operating state | `heat_pump_sub_status` | `5473` | - | Detailed heat pump operating state, such as heating, cooling, defrosting, or alarm. |
| HP: Mode | `heat_pump_mode` | `5006` | - | Current heat pump mode: heating or cooling. |
| HP: Remaining blocking time | `heat_pump_lockout_time` | `5572` | min | Remaining heat pump lockout time. |
| HP: Defrost status | `heat_pump_defrost_status` | `5626` | On/off | On/off state of the component. |
| HP: Compressor status | `heat_pump_compressor_status` | `5625` | On/off | On/off state of the component. |
| HP: Error status | `heat_pump_error_status` | `5002` | On/off | On/off state of the component. |
| HP: Release signal | `heat_pump_enable_signal` | `5004` | On/off | On/off state of the component. |
| HP: Compressor cut-off | `heat_pump_compressor_lock` | `5005` | On/off | On/off state of the component. |
| HP: Blocking signal | `heat_pump_lock_signal` | `5174` | - | Indicates whether the blocking signal blocks or releases the heat pump. |
| HP: Compressor frequency | `heat_pump_compressor_frequency` | `5205` | Hz | Current compressor frequency. |
| Fan state (outdoor) | `fan_state` | `5135` | On/off | On/off state of the component. |
| HP: Discharge pipe temp. | `heat_pump_hot_gas_temperature` | `5146` | °C | Measured discharge gas temperature of the heat pump. |
| Power | `power` | `5320` | W | Current electrical power consumption of the heat pump. |
| Thermal power | `power_thermal` | `5321` | W | Current thermal output of the heat pump. |
| Compressor starts | `compressor_starts` | `5822` | – | Number of compressor starts. |
| HP: Runtime (minutes) | `heat_pump_runtime_minutes` | `5823` | min | Heat pump runtime in minutes. |
| Runtime | `runtime_hours` | `5824` | h | Cumulative heat pump operating-hours counter. |
| HP: 4-way valve | `heat_pump_four_way_valve` | `5136` | On/off | On/off state of the component. |
| Electrical energy (hour) | `energy_electrical_hour` | `5388` | kWh | Electrical energy consumption for the stated period. |
| Electrical energy (day) | `energy_electrical_day` | `5293` | kWh | Electrical energy consumption for the stated period. |
| Electrical energy (week) | `energy_electrical_week` | `5294` | kWh | Electrical energy consumption for the stated period. |
| Electrical energy (month) | `energy_electrical_month` | `5295` | kWh | Electrical energy consumption for the stated period. |
| Electrical energy (year) | `energy_electrical_year` | `5296` | kWh | Electrical energy consumption for the stated period. |
| Electrical energy (hour, temporary) | `energy_electrical_hour_temporary` | `5389` | kWh | Internal hourly value with four decimal places; marked as diagnostic. |
| Calculated energy | `energy_electrical` | `5105` | kWh | Total consumption calculated locally from electrical power; ID 5105 supplies the initial value. |
| Electrical energy (Device) | `energy_electrical_raw` | `5105` | kWh | Direct device energy counter; disabled by default. |

Some target and diagnostic values may be disabled by default in Home Assistant.

### Electrical energy calculation

The **Calculated energy** entity (`energy_electrical`) is a total energy counter
maintained by the integration. REMKO provides its own energy counter as ID
`5105`, but that value is not always reliable for continuous use. The integration
therefore uses ID `5105` primarily as an initial or reference value and calculates
subsequent consumption from the heat pump's current electrical power, ID `5320`.

The energy between two successful updates is calculated using the trapezoidal
rule:

```text
additional energy [kWh]
  = (previous power [W] + current power [W]) / 2
    × time difference [h] / 1000
```

Averaging the previous and current power readings accounts for changes between
updates more accurately than using only one measurement. If a power reading is
missing, the existing energy total is retained. If a data gap exceeds four times
the configured polling interval, no energy is added for that interval, preventing
unrealistic jumps.

The calculated total is stored locally by Home Assistant: the first valid value
is saved immediately, subsequent changes are saved every ten minutes, and pending
changes are saved when the integration shuts down. After a restart, calculation
continues from the stored value. If no valid stored value exists, the direct REMKO
counter `5105` is used as the starting value. It remains separately available as
the disabled-by-default diagnostic entity **Electrical energy (Device)**
(`energy_electrical_raw`).

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
