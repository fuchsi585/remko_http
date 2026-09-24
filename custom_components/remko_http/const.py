"""Constants for Remko Heatpump integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Final

from homeassistant.components.sensor import (
    EntityCategory,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)

# Conditional import für UnitOfRatio (nur ab HA 2026.7)
try:
    from homeassistant.const import UnitOfRatio

    UNIT_PERCENTAGE = UnitOfRatio.PERCENTAGE
except ImportError:
    # Fallback für ältere HA-Versionen
    UNIT_PERCENTAGE = "%"

from .remko_enums import (
    CirculationDemandState,
    DeviceValue,
    HeatingCircuitStatus,
    HeatPumpLockSignal,
    HeatPumpMode,
    HeatPumpStatus,
    HeatPumpSubStatus,
    HotWaterReqState,
    OperatingState,
    RemkoDataType,
    RoomClimateMode,
    ScaleType,
    SwitchState,
)

CONF_HOST: Final = "host"
CONF_SCAN_INTERVAL: Final = "scan_interval"

DOMAIN: Final = "remko_http"
DEFAULT_SCAN_INTERVAL: Final = 20  # seconds
SLEEP_TIME_AFTER_SET_REQ: Final = 0.4

HTTP_REQ_SERIAL_NUMBER: Final = 5700
HTTP_TIMEOUT: Final = 15
MAX_DIFF_TIME_ENERGY_FACTOR: Final = 4  # scan_intervall * MAX_DIFF_TIME_ENERGY_FACTOR
STORAGE_VERSION: Final = 1
STORAGE_KEYS: tuple[str, ...] = ("energy_electrical",)

DEVICE_INFO_KEYS: dict[str, int | str] = {
    "model": 5198,
    "serial_number": 5700,
}


@dataclass(frozen=True)
class RemkoButtonDef:
    key: str
    read_key: str
    unit: str | None = None
    icon: str | None = None
    http_req: int | None = None
    option: type[Enum] | None = None
    disabled_by_default: bool = False
    data_type: RemkoDataType | None = None
    scale_type: ScaleType | None = None
    reset_delay: int | None = None
    availability: Callable[[dict[str, DeviceValue]], bool] | None = None


BUTTONS: list[RemkoButtonDef] = [
    RemkoButtonDef(
        key="action_heat_warm_water",
        read_key="action_heat_warm_water",
        icon="mdi:heat-wave",
        http_req=5693,
        option=SwitchState,
        data_type=RemkoDataType.UINT8,
        reset_delay=1,
        availability=lambda data: (
            data["water_temp_req"].phys_value is not None
            and data["water_temp"].phys_value is not None
            and data["hot_water_req_state"].phys_value is not None
            and data["hot_water_req_state"].phys_value == HotWaterReqState.STANDBY
            and data["water_temp"].phys_value < data["water_temp_req"].phys_value
        ),
    ),
]


@dataclass(frozen=True)
class RemkoSelectDef:
    key: str
    read_key: str
    unit: str | None = None
    icon: str | None = None
    http_req: int | None = None
    option: type[Enum] | None = None
    disabled_by_default: bool = False
    scale_type: ScaleType = ScaleType.DEFAULT


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
    option: type[Enum] | None = None
    disabled_by_default: bool = False
    data_type: RemkoDataType = RemkoDataType.UINT16
    scale_type: ScaleType = ScaleType.DEFAULT


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
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
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
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
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
    display_precision: int = 1
    http_req: int | None = None
    disabled_by_default: bool = False
    option: type[Enum] | None = None
    data_type: RemkoDataType = RemkoDataType.UINT16
    scale_type: ScaleType = ScaleType.DEFAULT


def _temperature_sensor(key: str, http_req: int) -> RemkoSensorDef:
    return RemkoSensorDef(
        key=key,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        http_req=http_req,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    )


def _switch_sensor(
    key: str, http_req: int, icon: str = "mdi:toggle-switch"
) -> RemkoSensorDef:
    return RemkoSensorDef(
        key=key,
        device_class=SensorDeviceClass.ENUM,
        icon=icon,
        http_req=http_req,
        option=SwitchState,
        data_type=RemkoDataType.INT8,
    )


def _measurement_sensor(
    key: str,
    http_req: int,
    unit: str | None = None,
    *,
    data_type: RemkoDataType = RemkoDataType.UINT16,
    scale_type: ScaleType = ScaleType.DEFAULT,
    display_precision: int = 0,
    icon: str | None = None,
) -> RemkoSensorDef:
    return RemkoSensorDef(
        key=key,
        unit=unit,
        state_class=SensorStateClass.MEASUREMENT,
        icon=icon,
        http_req=http_req,
        data_type=data_type,
        scale_type=scale_type,
        display_precision=display_precision,
    )


SENSORS: tuple[RemkoSensorDef, ...] = (
    # Übersicht
    RemkoSensorDef(
        key="cold_hotter_state",
        unit=UnitOfTemperature.KELVIN,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        http_req=1946,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
    RemkoSensorDef(
        key="room_climate_mode",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:state-machine",
        http_req=1088,
        option=RoomClimateMode,
        data_type=RemkoDataType.UINT8,
    ),
    RemkoSensorDef(
        key="operating_status",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:state-machine",
        http_req=5001,
        option=OperatingState,
        data_type=RemkoDataType.INT8,
    ),
    # Warmwasser
    RemkoSensorDef(
        key="water_temp_req",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        disabled_by_default=True,
        http_req=1082,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
    _temperature_sensor("hot_water_target_temperature", 5038),
    RemkoSensorDef(
        key="water_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        http_req=5039,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
    RemkoSensorDef(
        key="hot_water_req_state",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:water-boiler",
        # entity_category=EntityCategory.DIAGNOSTIC,
        http_req=5064,
        option=HotWaterReqState,
        data_type=RemkoDataType.INT8,
    ),
    _switch_sensor("hot_water_diverter_valve", 5162, "mdi:valve"),
    _measurement_sensor(
        "hot_water_energy",
        5376,
        UnitOfEnergy.KILO_WATT_HOUR,
        data_type=RemkoDataType.UINT32,
        icon="mdi:water-boiler",
    ),
    RemkoSensorDef(
        key="hot_water_hygiene_function",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:water-check",
        http_req=5803,
        option=HotWaterReqState,
        data_type=RemkoDataType.INT8,
    ),
    RemkoSensorDef(
        key="hot_water_circulation_demand",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:pump",
        http_req=5133,
        option=CirculationDemandState,
        data_type=RemkoDataType.INT8,
    ),
    _temperature_sensor("hot_water_circulation_target_temperature", 5041),
    RemkoSensorDef(
        key="circulation_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        http_req=5027,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
    RemkoSensorDef(
        key="circulation_pump_state",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:pump",
        http_req=5151,
        option=SwitchState,
        data_type=RemkoDataType.INT8,
    ),
    # Hydraulik
    RemkoSensorDef(
        key="hydraulics_demand",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:hvac",
        http_req=5040,
        option=RoomClimateMode,
        data_type=RemkoDataType.UINT8,
    ),
    RemkoSensorDef(
        key="heating_req_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        http_req=5085,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
    RemkoSensorDef(
        key="heating_actual_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        http_req=5190,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
    RemkoSensorDef(
        key="hydraulics_thermal_power",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        http_req=5232,
        scale_type=ScaleType.POWER,
        display_precision=0,
    ),
    RemkoSensorDef(
        key="mixed_flow_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        http_req=5741,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
    RemkoSensorDef(
        key="mixed_return_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        http_req=5476,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
    _measurement_sensor(
        "hydraulics_target_flow_rate",
        5073,
        "l/min",
        scale_type=ScaleType.TENTH,
        display_precision=1,
        icon="mdi:water",
    ),
    _measurement_sensor(
        "hydraulics_actual_flow_rate",
        5582,
        "l/min",
        scale_type=ScaleType.TENTH,
        display_precision=1,
        icon="mdi:water",
    ),
    _measurement_sensor(
        "hydraulics_actual_flow_rate_mixed",
        5740,
        "l/min",
        scale_type=ScaleType.TENTH,
        display_precision=1,
        icon="mdi:water",
    ),
    _measurement_sensor(
        "hydraulics_pump_speed", 5575, UNIT_PERCENTAGE, icon="mdi:pump"
    ),
    RemkoSensorDef(
        key="hydraulics_heating_energy",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        http_req=5374,
        data_type=RemkoDataType.UINT32,
        display_precision=0,
    ),
    RemkoSensorDef(
        key="hydraulics_cooling_energy",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        http_req=5010,
        data_type=RemkoDataType.UINT32,
        display_precision=0,
    ),
    _switch_sensor("hydraulics_cooling_diverter_valve", 5166, "mdi:valve"),
    RemkoSensorDef(
        key="out_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        http_req=5032,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
    # Allgemeine Heizkreiswerte
    RemkoSensorDef(
        key="mixed_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        http_req=5055,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
    RemkoSensorDef(
        key="room_temp_req",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        http_req=5075,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
    RemkoSensorDef(
        key="room_temp_act",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        http_req=5050,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
    RemkoSensorDef(
        key="room_humidity",
        unit=UNIT_PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cloud-percent",
        http_req=5066,
        display_precision=0,
    ),
    RemkoSensorDef(
        key="pump_speed",
        unit=UNIT_PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:pump",
        http_req=5576,  # 5043 - abs in rpm?
        display_precision=0,
    ),
    # Ungemischter Heizkreis
    RemkoSensorDef(
        key="heating_circuit_unmixed_operating_mode",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:hvac",
        http_req=5069,
        option=RoomClimateMode,
        data_type=RemkoDataType.UINT8,
    ),
    _temperature_sensor("heating_circuit_unmixed_target_temperature", 5033),
    _temperature_sensor("heating_circuit_unmixed_actual_temperature", 5034),
    _temperature_sensor("heating_circuit_unmixed_dew_point", 5070),
    RemkoSensorDef(
        key="heating_circuit_unmixed_status",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:state-machine",
        http_req=5710,
        option=HeatingCircuitStatus,
        data_type=RemkoDataType.UINT8,
    ),
    _temperature_sensor("heating_circuit_unmixed_setpoint_adjustment", 5717),
    # Wärmepumpe / Außengerät
    RemkoSensorDef(
        key="heat_pump_status",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:heat-pump",
        http_req=5049,
        option=HeatPumpStatus,
        data_type=RemkoDataType.UINT8,
    ),
    RemkoSensorDef(
        key="heat_pump_sub_status",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:state-machine",
        http_req=5473,
        option=HeatPumpSubStatus,
        data_type=RemkoDataType.UINT8,
    ),
    RemkoSensorDef(
        key="heat_pump_mode",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:hvac",
        http_req=5006,
        option=HeatPumpMode,
        data_type=RemkoDataType.INT8,
    ),
    _measurement_sensor(
        "heat_pump_lockout_time",
        5572,
        UnitOfTime.MINUTES,
        icon="mdi:timer-outline",
    ),
    _switch_sensor("heat_pump_defrost_status", 5626, "mdi:snowflake-melt"),
    _switch_sensor("heat_pump_compressor_status", 5625, "mdi:engine"),
    _switch_sensor("heat_pump_error_status", 5002, "mdi:alert-circle"),
    _switch_sensor("heat_pump_enable_signal", 5004, "mdi:check-circle"),
    _switch_sensor("heat_pump_compressor_lock", 5005, "mdi:lock"),
    RemkoSensorDef(
        key="heat_pump_lock_signal",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:lock-alert",
        http_req=5174,
        option=HeatPumpLockSignal,
        data_type=RemkoDataType.INT8,
    ),
    _measurement_sensor(
        "heat_pump_compressor_frequency", 5205, "Hz", icon="mdi:sine-wave"
    ),
    RemkoSensorDef(
        key="heat_pump_current",
        unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-ac",
        entity_category=EntityCategory.DIAGNOSTIC,
        display_precision=1,
        http_req=5138,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TENTH,
    ),
    RemkoSensorDef(
        key="auxiliary_heat_generator_mains_voltage",
        unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
        entity_category=EntityCategory.DIAGNOSTIC,
        display_precision=2,
        http_req=5796,
        data_type=RemkoDataType.UINT16,
        scale_type=ScaleType.HUNDREDTH,
    ),
    RemkoSensorDef(
        key="fan_state",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:fan",
        http_req=5135,
        option=SwitchState,
        data_type=RemkoDataType.INT8,
    ),
    _temperature_sensor("heat_pump_hot_gas_temperature", 5146),
    RemkoSensorDef(
        key="power",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
        display_precision=0,
        http_req=5320,
        scale_type=ScaleType.POWER,
    ),
    RemkoSensorDef(
        key="power_thermal",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fire",
        display_precision=0,
        http_req=5321,
        scale_type=ScaleType.POWER,
    ),
    RemkoSensorDef(
        key="compressor_starts",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:counter",
        display_precision=0,
        http_req=5822,
    ),
    _measurement_sensor(
        "heat_pump_runtime_minutes",
        5823,
        UnitOfTime.MINUTES,
        icon="mdi:timer-outline",
    ),
    RemkoSensorDef(
        key="runtime_hours",
        unit=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:timer-outline",
        display_precision=0,
        http_req=5824,
    ),
    _switch_sensor("heat_pump_four_way_valve", 5136, "mdi:valve"),
    # Elektrische Energie nach Zeitraum
    RemkoSensorDef(
        key="energy_electrical_hour",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
        display_precision=0,
        http_req=5388,
        data_type=RemkoDataType.UINT32,
    ),
    RemkoSensorDef(
        key="energy_electrical_day",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
        display_precision=0,
        http_req=5293,
        data_type=RemkoDataType.UINT32,
    ),
    RemkoSensorDef(
        key="energy_electrical_week",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
        display_precision=0,
        http_req=5294,
        data_type=RemkoDataType.UINT32,
    ),
    RemkoSensorDef(
        key="energy_electrical_month",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
        display_precision=0,
        http_req=5295,
        data_type=RemkoDataType.UINT32,
    ),
    RemkoSensorDef(
        key="energy_electrical_year",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:lightning-bolt",
        display_precision=0,
        http_req=5296,
        data_type=RemkoDataType.UINT32,
    ),
    RemkoSensorDef(
        key="energy_electrical_hour_temporary",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:lightning-bolt",
        entity_category=EntityCategory.DIAGNOSTIC,
        display_precision=4,
        http_req=5389,
        data_type=RemkoDataType.UINT32,
        scale_type=ScaleType.TEN_THOUSANDTH,
    ),
)

# binary_sensor:
#   5051 - "heat_gen_status": ["Heat generator status", "Wärmeerzeuger Status"]


@dataclass(frozen=True)
class RemkoEnergySensorDef:
    key: str
    unit: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    icon: str | None = None
    entity_category: str | None = None
    display_precision: int = 2
    http_req: int | None = None
    disabled_by_default: bool = False
    option: type[Enum] | None = None
    data_type: RemkoDataType = RemkoDataType.UINT32
    scale_type: ScaleType = ScaleType.DEFAULT
    integrated_power: str | None = None
    source_key: str | None = None
    max_energy_stored_diff: int | None = None


ENERGY_SENSORS: tuple[RemkoEnergySensorDef, ...] = (
    RemkoEnergySensorDef(
        key="energy_electrical",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower",
        http_req=5105,
        data_type=RemkoDataType.UINT32,
        integrated_power="power",
        source_key="energy_electrical_raw",
        max_energy_stored_diff=2,
    ),
)

ENERGY_SENSORS_DEVICE_RAW: tuple[RemkoEnergySensorDef, ...] = (
    RemkoEnergySensorDef(
        key="energy_electrical_raw",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower",
        entity_category=EntityCategory.DIAGNOSTIC,
        display_precision=2,
        http_req=5105,
        data_type=RemkoDataType.UINT32,
        disabled_by_default=True,
    ),
)

HTTP_REQS: Final = list(
    {
        definition.http_req
        for definition in (
            *BUTTONS,
            *SELECTORS,
            *SENSORS,
            *NUMBERS,
            *ENERGY_SENSORS,
            *ENERGY_SENSORS_DEVICE_RAW,
        )
        if definition.http_req is not None
    }
)

# "heating_circ_mode": 1972,  # switch
