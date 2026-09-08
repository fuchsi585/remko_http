"""Tests for Remko Heatpump constants."""

from custom_components.remko_http.const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ENERGY_SENSORS,
    ENERGY_SENSORS_DEVICE_RAW,
    HTTP_REQ_SERIAL_NUMBER,
    HTTP_REQS,
    NUMBERS,
    SELECTORS,
    SENSORS,
    SLEEP_TIME_AFTER_SET_REQ,
    RemkoNumberDef,
    RemkoSelectDef,
    RemkoSensorDef,
)
from custom_components.remko_http.remko_enums import (
    RemkoDataType,
    ScaleType,
)


def test_constants() -> None:
    """Test integration constants."""
    assert CONF_HOST == "host"
    assert CONF_SCAN_INTERVAL == "scan_interval"
    assert DOMAIN == "remko_http"
    assert DEFAULT_SCAN_INTERVAL == 20
    assert SLEEP_TIME_AFTER_SET_REQ == 0.4
    assert HTTP_REQ_SERIAL_NUMBER == 5700


def test_data_types() -> None:
    """Test protocol data types."""
    assert RemkoDataType.UINT8.response_size == 1
    assert RemkoDataType.INT16.response_size == 2
    assert RemkoDataType.INT16.signed is True
    assert RemkoDataType.UINT32.response_size == 4
    assert RemkoDataType.UINT32.signed is False


def test_scale_types() -> None:
    """Test protocol scaling factors."""
    assert ScaleType.DEFAULT.scale == 1
    assert ScaleType.TEMPERATURE.scale == 0.1
    assert ScaleType.POWER.scale == 100


def test_selectors() -> None:
    """Test select definitions."""
    assert len(SELECTORS) == 1
    definition = SELECTORS[0]
    assert isinstance(definition, RemkoSelectDef)
    assert definition.key == "set_room_climate_mode"
    assert definition.read_key == "room_climate_mode"
    assert definition.http_req == 1088


def test_numbers() -> None:
    """Test number definitions."""
    assert len(NUMBERS) == 2
    cold_hotter = NUMBERS[0]
    assert isinstance(cold_hotter, RemkoNumberDef)
    assert cold_hotter.key == "set_cold_hotter"
    assert cold_hotter.read_key == "cold_hotter_state"
    assert cold_hotter.http_req == 1946

    water_temp = NUMBERS[1]
    assert isinstance(water_temp, RemkoNumberDef)
    assert water_temp.key == "set_water_temp_req"
    assert water_temp.read_key == "water_temp_req"
    assert water_temp.http_req == 1082


def test_sensors_are_unique_by_key() -> None:
    """Test that sensor keys are unique."""
    keys = [sensor.key for sensor in SENSORS]
    assert len(keys) == len(set(keys))


def test_sensors_have_http_request() -> None:
    """Test that all sensors have an HTTP request."""
    assert all(sensor.http_req is not None for sensor in SENSORS)


def test_sensor_definitions() -> None:
    """Test sensor definitions."""
    assert all(isinstance(sensor, RemkoSensorDef) for sensor in SENSORS)

    power = next(sensor for sensor in SENSORS if sensor.key == "power")
    assert power.http_req == 5320

    operating_status = next(
        sensor for sensor in SENSORS if sensor.key == "operating_status"
    )
    assert operating_status.http_req == 5001


def test_energy_sensor_definitions() -> None:
    """Test calculated and raw energy sensor definitions."""
    assert len(ENERGY_SENSORS) == 1
    assert len(ENERGY_SENSORS_DEVICE_RAW) == 1

    calculated = ENERGY_SENSORS[0]
    raw = ENERGY_SENSORS_DEVICE_RAW[0]

    assert calculated.key == "energy_electrical"
    assert calculated.http_req == 5105
    assert calculated.is_calculated is True

    assert raw.key == "energy_electrical_raw"
    assert raw.http_req == 5105
    assert raw.disabled_by_default is True


def test_http_requests_are_unique() -> None:
    """Test that all HTTP request IDs are unique."""
    assert len(HTTP_REQS) == len(set(HTTP_REQS))


def test_http_requests_contain_all_definitions() -> None:
    """Test that all configured HTTP requests are collected."""
    expected = {
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
    assert set(HTTP_REQS) == expected
