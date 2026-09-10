"""Constants for Remko Heatpump integration."""

from dataclasses import dataclass
from enum import Enum
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

from .remko_enums import (
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
MAX_DIFF_TIME_ENERGY_FACTOR: Final = 4  # scan_intervall * factor
STORAGE_VERSION: Final = 1
STORAGE_KEYS: tuple[str, ...] = ("energy_electrical",)


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
    enable_key: str | None = None
    enable_value: type[Enum] | None = None


BUTTONS: list[RemkoButtonDef] = [
    RemkoButtonDef(
        key="action_heat_warm_water",
        read_key="action_heat_warm_water",
        icon="mdi:heat-wave",
        http_req=5693,
        option=SwitchState,
        data_type=RemkoDataType.UINT8,
        reset_delay=1,
        enable_key="hot_water_req_state",
        enable_value=HotWaterReqState.STANDBY,
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


SENSORS: tuple[RemkoSensorDef, ...] = (
    RemkoSensorDef(
        key="cold_hotter_state",
        unit=UnitOfTemperature.KELVIN,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        http_req=1946,
        disabled_by_default=True,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
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
        key="mixed_return_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-water",
        http_req=5476,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
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
        key="out_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        http_req=5032,
        data_type=RemkoDataType.INT16,
        scale_type=ScaleType.TEMPERATURE,
    ),
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
        unit=UnitOfRatio.PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cloud-percent",
        http_req=5066,
        display_precision=0,
    ),
    RemkoSensorDef(
        key="pump_speed",
        unit=UnitOfRatio.PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:pump",
        http_req=5576,  # 5043 - abs in rpm?
        display_precision=0,
    ),
    RemkoSensorDef(
        key="power_own_use",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
        display_precision=0,
        http_req=5231,
        scale_type=ScaleType.POWER,
        disabled_by_default=True,
    ),
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
        icon="mdi:flash",
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
    RemkoSensorDef(
        key="runtime_hours",
        unit=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:counter",
        display_precision=0,
        http_req=5824,
    ),
    RemkoSensorDef(
        key="operating_status",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:cog",
        # entity_category=EntityCategory.DIAGNOSTIC,
        http_req=5001,
        option=OperatingState,
        data_type=RemkoDataType.UINT8,
    ),
    RemkoSensorDef(
        key="hot_water_req_state",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:water-boiler",
        # entity_category=EntityCategory.DIAGNOSTIC,
        http_req=5064,
        option=HotWaterReqState,
        data_type=RemkoDataType.UINT8,
    ),
    RemkoSensorDef(
        key="circulation_pump_state",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:water",
        # entity_category=EntityCategory.DIAGNOSTIC,
        http_req=5151,
        option=SwitchState,
        data_type=RemkoDataType.UINT8,
    ),
    RemkoSensorDef(
        key="room_climate_mode",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:cog",
        http_req=1088,
        disabled_by_default=True,
        # entity_category=EntityCategory.DIAGNOSTIC,
        option=RoomClimateMode,
        data_type=RemkoDataType.UINT8,
    ),
    RemkoSensorDef(
        key="fan_state",
        device_class=SensorDeviceClass.ENUM,
        # entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:fan",
        http_req=5135,
        option=SwitchState,
        data_type=RemkoDataType.UINT8,
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
    intergrated_power: str | None = None
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
        intergrated_power="power",
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
