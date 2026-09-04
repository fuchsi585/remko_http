"""Constants for Remko Heatpump integration."""

from enum import Enum
from dataclasses import dataclass
from homeassistant.const import Platform

CONF_HOST = "host"
CONF_SCAN_INTERVAL = "scan_interval"

PLATFORMS: list[Platform] = [Platform.NUMBER, Platform.SELECT, Platform.SENSOR]

DOMAIN = "remko_http"
DEFAULT_SCAN_INTERVAL = 20  # seconds
SLEEP_TIME_AFTER_SET_REQ = 0.4


class Factor(float, Enum):
    TEMP = 0.1
    POWER = 100
    POWER_KWH = 0.001


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


@dataclass(frozen=True)
class RemkoSelectDef:
    key: str
    state_key: str
    unit: str | None = None
    icon: str | None = None
    http_req: int | None = None


@dataclass(frozen=True)
class RemkoNumberDef:
    key: str
    state_key: str
    device_class: str | None = None
    unit: str | None = None
    icon: str | None = None
    min_value: float = 0
    max_value: float = 100
    step: float = 1
    http_req: int | None = None


@dataclass(frozen=True)
class RemkoSwitchDef:
    key: str
    state_key: str
    unit: str | None = None
    icon: str | None = None
    http_req: int | None = None


SWITCHES: list[RemkoSwitchDef] = [
    RemkoSwitchDef("set_action_heat_warm_water", "", "", http_req=5693)
]

SELECTORS: list[RemkoSelectDef] = [
    RemkoSelectDef(
        "set_room_climate_mode",
        "room_climate_mode",
        "mdi:home",
        http_req=1088,
    ),
]

NUMBERS: list[RemkoNumberDef] = [
    RemkoNumberDef(
        "set_cold_hotter",
        "cold_hotter_state",
        "temperature",
        "K",
        "mdi:home-thermometer",
        min_value=0,
        max_value=3,
        step=0.5,
        http_req=1946,
    ),
    RemkoNumberDef(
        "set_water_temp_req",
        "water_temp_req",
        "temperature",
        "°C",
        "mdi:thermometer-water",
        min_value=35,
        max_value=80,
        step=0.5,
        http_req=1082,
    ),
]

SENSORS: list[RemkoSensorDef] = [
    RemkoSensorDef(
        "cold_hotter_state",
        "K",
        "temperature",
        "measurement",
        "mdi:thermometer",
        http_req=1946,
        disabled_by_default=True,
    ),
    RemkoSensorDef(
        "water_temp_req",
        "°C",
        "temperature",
        "measurement",
        "mdi:thermometer-water",
        disabled_by_default=True,
        http_req=1082,
    ),
    RemkoSensorDef(
        "water_temp",
        "°C",
        "temperature",
        "measurement",
        "mdi:thermometer-water",
        http_req=5039,
    ),
    RemkoSensorDef(
        "heating_req_temp",
        "°C",
        "temperature",
        "measurement",
        "mdi:thermometer-water",
        http_req=5085,
    ),
    RemkoSensorDef(
        "heating_actual_temp",
        "°C",
        "temperature",
        "measurement",
        "mdi:thermometer-water",
        http_req=5190,
    ),
    RemkoSensorDef(
        "circulation_temp",
        "°C",
        "temperature",
        "measurement",
        "mdi:thermometer-water",
        http_req=5027,
    ),
    RemkoSensorDef(
        "out_temp",
        "°C",
        "temperature",
        "measurement",
        "mdi:thermometer",
        http_req=5032,
    ),
    RemkoSensorDef(
        "mixed_temp",
        "°C",
        "temperature",
        "measurement",
        "mdi:thermometer",
        http_req=5055,
    ),
    RemkoSensorDef(
        "room_temp_req",
        "°C",
        "temperature",
        "measurement",
        "mdi:thermometer",
        http_req=5075,
    ),
    RemkoSensorDef(
        "room_temp_act",
        "°C",
        "temperature",
        "measurement",
        "mdi:thermometer",
        http_req=5050,
    ),
    RemkoSensorDef(
        "room_humidity",
        "%",
        "humidity",
        "measurement",
        "mdi:cloud-percent",
        http_req=5066,
        display_precision=0,
    ),
    # --- Power and Energy
    RemkoSensorDef(
        "power",
        "W",
        "power",
        "measurement",
        "mdi:transmission-tower",
        display_precision=0,
        http_req=5320,
    ),
    RemkoSensorDef(
        "power_thermal",
        "W",
        "power",
        "measurement",
        "mdi:flash",
        display_precision=0,
        http_req=5321,
    ),
    RemkoSensorDef(
        "energy_electical",
        "kWh",
        "energy",
        "total_increasing",
        "mdi:transmission-tower",
        display_precision=0,
        http_req=5105,
    ),
    RemkoSensorDef(
        "compressor_starts",
        None,
        None,
        "measurement",
        "mdi:counter",
        # entity_category="diagnostic",
        display_precision=0,
        http_req=5822,
    ),
    RemkoSensorDef(
        "runtime_hours",
        "h",
        "duration",
        "total_increasing",
        "mdi:counter",
        # entity_category="diagnostic",
        display_precision=0,
        http_req=5824,
    ),
    # -- Diagnostics
    RemkoSensorDef(
        "operating_status",
        None,
        "enum",
        None,
        "mdi:cog",
        entity_category="diagnostic",
        http_req=5001,
    ),
    RemkoSensorDef(
        "hot_water_req_state",
        None,
        "enum",
        None,
        "mdi:water-boiler",
        entity_category="diagnostic",
        http_req=5064,
    ),
    RemkoSensorDef(
        "circulation_pump_state",
        None,
        "enum",
        None,
        "mdi:water",
        entity_category="diagnostic",
        http_req=5151,
    ),
    RemkoSensorDef(
        "room_climate_mode",
        None,
        "enum",
        None,
        "mdi:cog",
        http_req=1088,
        disabled_by_default=True,
        entity_category="diagnostic",
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
]

AVAILABLE_SENSOR_QUERIES = [definition.http_req for definition in SENSORS]
# AVAILABLE_SWITCH_QUERIES = [definition.http_req for definition in SWITCHES]
AVAILABLE_NUMBER_QUERIES = [definition.http_req for definition in NUMBERS]
AVAILABLE_SELECT_QUERIES = [definition.http_req for definition in SELECTORS]


def _get_all_queries():
    queries = set(AVAILABLE_NUMBER_QUERIES)
    queries.update(AVAILABLE_SENSOR_QUERIES)
    # queries.update(AVAILABLE_SWITCH_QUERIES)
    queries.update(AVAILABLE_SELECT_QUERIES)

    return list(queries)


ALL_QUERIES = _get_all_queries()

STATE_MAPPING = {
    # 1079: {  # hot_water_op_mode
    #     "00": "Automatik Komfort",
    #     "01": "Automatik Eco",
    #     "02": "Solar/PV",
    #     "03": "Aus",
    # },
    5064: {"00": "standby", "01": "active"},
    1088: {
        "01": "auto",
        "02": "heating",
        "03": "standby",
        "04": "cooling",
    },
    5001: {  # operating_status
        "00": "unknown",  # "Blocked",
        "01": "fault",
        "02": "defrosting",  # "Defrosting",
        "03": "defrost_buffer",  # "Loading defrost buffer",
        "04": "dhw_buffer",  # "Loading DHW",
        "05": "energy_storage",
        "06": "heating",  # "Heating",
        "07": "cooling",  # "Cooling",
        "09": "circulation",  # Idle
        "0A": "standby",
        "0C": "frost_protection",  # "Frost Protection",
        "40": "ready",
    },
    5151: {"00": "off", "01": "on"},
}

# "heating_circ_mode": 1972,  # switch
