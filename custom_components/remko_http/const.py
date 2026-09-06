"""Constants for Remko Heatpump integration."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from homeassistant.components.sensor import (
    EntityCategory,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfPower,
    UnitOfRatio,
    UnitOfTemperature,
    UnitOfTime,
)

CONF_HOST: Final = "host"
CONF_SCAN_INTERVAL: Final = "scan_interval"

DOMAIN: Final = "remko_http"
DEFAULT_SCAN_INTERVAL: Final = 20  # seconds
SLEEP_TIME_AFTER_SET_REQ: Final = 0.4

HTTP_REQ_SERIAL_NUMBER: Final = 5700


class ConvData(StrEnum):
    TEMPERATURE = SensorDeviceClass.TEMPERATURE
    POWER = SensorDeviceClass.POWER

    @property
    def scale(self) -> float | int:
        return {SensorDeviceClass.TEMPERATURE: 0.001, SensorDeviceClass.POWER: 100}[
            self
        ]

    @property
    def data_type(self) -> int:
        return {SensorDeviceClass.TEMPERATURE: float, SensorDeviceClass.POWER: int}[
            self
        ]


class RoomClimateMode(StrEnum):
    AUTO = "auto"
    HEATING = "heating"
    STANDBY = "standby"
    COOLING = "cooling"

    @property
    def hex_value(self) -> str | None:
        try:
            return {
                RoomClimateMode.AUTO: "01",
                RoomClimateMode.HEATING: "02",
                RoomClimateMode.STANDBY: "03",
                RoomClimateMode.COOLING: "04",
            }[self]
        except KeyError:
            return None

    @classmethod
    def from_hex(cls, value: str) -> "RoomClimateMode | str":
        for state in cls:
            if state.hex_value == value:
                return state

        return f"Status N/A: {value}"


class HotWaterReqState(StrEnum):
    STANDBY = "standby"
    ACTIVE = "active"

    @property
    def hex_value(self) -> str | None:
        try:
            return {
                HotWaterReqState.STANDBY: "00",
                HotWaterReqState.ACTIVE: "01",
            }[self]
        except KeyError:
            return None

    @classmethod
    def from_hex(cls, value: str) -> "HotWaterReqState | str":
        for state in cls:
            if state.hex_value == value:
                return state

        return f"Status N/A: {value}"


class PumpState(StrEnum):
    OFF = "off"
    ON = "on"

    @property
    def hex_value(self) -> str | None:
        try:
            return {
                PumpState.OFF: "00",
                PumpState.ON: "01",
            }[self]
        except KeyError:
            return None

    @classmethod
    def from_hex(cls, value: str) -> "PumpState | str":
        for state in cls:
            if state.hex_value == value:
                return state

        return f"Status N/A: {value}"


class OperatingState(StrEnum):
    UNKNOWN = "unknown"
    FAULT = "fault"
    DEFROST = "defrosting"
    DEFROSTBUFFER = "defrost_buffer"
    DHWBUFFER = "dhw_buffer"
    ENERGYSTORAGE = "energy_storage"
    HEATING = "heating"
    COOLING = "cooling"
    CIRCULATION = "circulation"
    STANDBY = "standby"
    FROSTPROTECT = "frost_protection"
    READY = "ready"

    @property
    def hex_value(self) -> str | None:
        try:
            return {
                OperatingState.UNKNOWN: "00",
                OperatingState.FAULT: "01",
                OperatingState.DEFROST: "02",
                OperatingState.DEFROSTBUFFER: "03",
                OperatingState.DHWBUFFER: "04",
                OperatingState.ENERGYSTORAGE: "05",
                OperatingState.HEATING: "06",
                OperatingState.COOLING: "07",
                OperatingState.CIRCULATION: "09",
                OperatingState.STANDBY: "0A",
                OperatingState.FROSTPROTECT: "0C",
                OperatingState.READY: "40",
            }[self]
        except ValueError:
            return None

    @classmethod
    def from_hex(cls, value: str) -> "OperatingState | str":
        for state in cls:
            if state.hex_value == value:
                return state

        return f"Status N/A: {value}"


# @dataclass(frozen=True)
# class RemkoSwitchDef:
#     key: str
#     state_key: str
#     unit: str | None = None
#     icon: str | None = None
#     http_req: int | None = None


# # SWITCHES: list[RemkoSwitchDef] = [
# #     RemkoSwitchDef("set_action_heat_warm_water", "", "", http_req=5693)
# # ]


@dataclass(frozen=True)
class RemkoSelectDef:
    key: str
    read_key: str
    unit: str | None = None
    icon: str | None = None
    http_req: int | None = None
    option: tuple[str, ...] | None = None
    disabled_by_default: bool = False
    scale: float | None = None


SELECTORS: tuple[RemkoSelectDef, ...] = (
    RemkoSelectDef(
        key="set_room_climate_mode",
        read_key="room_climate_mode",
        icon="mdi:home",
        http_req=1088,
        option=RoomClimateMode,
    ),
)


@dataclass(frozen=True)
class RemkoNumberDef:
    key: str
    read_key: str
    min_value: float = 0
    max_value: float = 100
    step: float = 1
    device_class: str | None = None
    unit: str | None = None
    icon: str | None = None
    http_req: int | None = None
    option: StrEnum | None = None
    disabled_by_default: bool = False
    scale: float | None = None


NUMBERS: tuple[RemkoNumberDef, ...] = (
    RemkoNumberDef(
        key="set_cold_hotter",
        read_key="cold_hotter_state",
        device_class=SensorDeviceClass.TEMPERATURE,
        unit=UnitOfTemperature.KELVIN,
        icon="mdi:home-thermometer",
        min_value=0,
        max_value=3,
        step=0.5,
        http_req=1946,
    ),
    RemkoNumberDef(
        key="set_water_temp_req",
        read_key="water_temp_req",
        device_class=SensorDeviceClass.TEMPERATURE,
        unit=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-water",
        min_value=35,
        max_value=80,
        step=0.5,
        http_req=1082,
    ),
)


@dataclass(frozen=True)
class RemkoSensorDef:
    key: str
    unit: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    icon: str | None = None
    entity_category: str | None = None
    display_precision: int | None = 1
    http_req: int | None = None
    disabled_by_default: bool = False
    option: tuple[str, ...] | None = None
    scale: float | None = None


SENSORS: tuple[RemkoSensorDef, ...] = (
    RemkoSensorDef(
        key="cold_hotter_state",
        unit=UnitOfTemperature.KELVIN,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        http_req=1946,
        disabled_by_default=True,
    ),
    RemkoSensorDef(
        key="water_temp_req",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        disabled_by_default=True,
        http_req=1082,
    ),
    RemkoSensorDef(
        key="water_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        http_req=5039,
    ),
    RemkoSensorDef(
        key="heating_req_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        http_req=5085,
    ),
    RemkoSensorDef(
        key="heating_actual_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        http_req=5190,
    ),
    RemkoSensorDef(
        key="circulation_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        http_req=5027,
    ),
    RemkoSensorDef(
        key="out_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        http_req=5032,
    ),
    RemkoSensorDef(
        key="mixed_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        http_req=5055,
    ),
    RemkoSensorDef(
        key="room_temp_req",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        http_req=5075,
    ),
    RemkoSensorDef(
        key="room_temp_act",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        http_req=5050,
    ),
    RemkoSensorDef(
        key="room_humidity",
        unit=UnitOfRatio.PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cloud-percent",
        http_req=5066,
        display_precision=0,
    ),
    # --- Power
    RemkoSensorDef(
        key="power",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
        display_precision=0,
        http_req=5320,
    ),
    RemkoSensorDef(
        key="power_thermal",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
        display_precision=0,
        http_req=5321,
    ),
    RemkoSensorDef(
        key="compressor_starts",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:counter",
        display_precision=0,
        http_req=5822,
    ),
    RemkoSensorDef(
        key="runtime_hours",
        unit=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:counter",
        display_precision=0,
        http_req=5824,
    ),
    # -- Diagnostics
    RemkoSensorDef(
        key="operating_status",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:cog",
        entity_category=EntityCategory.DIAGNOSTIC,
        http_req=5001,
        option=OperatingState,
    ),
    RemkoSensorDef(
        key="hot_water_req_state",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:water-boiler",
        entity_category=EntityCategory.DIAGNOSTIC,
        http_req=5064,
        option=HotWaterReqState,
    ),
    RemkoSensorDef(
        key="circulation_pump_state",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:water",
        entity_category=EntityCategory.DIAGNOSTIC,
        http_req=5151,
        option=PumpState,
    ),
    RemkoSensorDef(
        key="room_climate_mode",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:cog",
        http_req=1088,
        disabled_by_default=True,
        entity_category=EntityCategory.DIAGNOSTIC,
        option=RoomClimateMode,
    ),
    # RemkoSensorDef(
    #     "action_state_heat_warm_water",
    #     "1 x WW aufheizen",
    #     None,
    #     "enum",
    #     None,
    #     "mdi:cog",
    #     http_req=5693,
    #     disabled_by_default=True,
    #     entity_category="diagnostic",
    # ),
)


@dataclass(frozen=True)
class RemkoEnergySensorDef:
    key: str
    unit: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    icon: str | None = None
    entity_category: str | None = None
    display_precision: int | None = 1
    http_req: int | None = None
    disabled_by_default: bool = False
    option: tuple[str, ...] | None = None
    is_calculated: bool = False
    scale: float | None = None


ENERGY_SENSORS: tuple[RemkoEnergySensorDef, ...] = (
    RemkoEnergySensorDef(
        key="energy_electrical",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower",
        display_precision=0,
        http_req=5105,
        is_calculated=True,
    ),
)

ENERGY_SENSORS_DEVICE_RAW: tuple[RemkoEnergySensorDef, ...] = (
    RemkoEnergySensorDef(
        key=f"{energy_sensor.key}_raw",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower",
        display_precision=0,
        http_req=5105,
    )
    for energy_sensor in ENERGY_SENSORS
    if energy_sensor.is_calculated
)

HTTP_REQS: Final = list(
    {
        definition.http_req
        for definition in (
            *SELECTORS,
            *SENSORS,
            *NUMBERS,
            *ENERGY_SENSORS,
            *ENERGY_SENSORS_DEVICE_RAW,
        )
        if definition.http_req is not None
    }
)


# 1079: {  # hot_water_op_mode
#     "00": "Automatik Komfort",
#     "01": "Automatik Eco",
#     "02": "Solar/PV",
#     "03": "Aus",
# },

# "heating_circ_mode": 1972,  # switch
