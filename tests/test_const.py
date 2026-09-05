"""Tests for Remko Heatpump constants."""

import pytest

from custom_components.remko_http.const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    HTTP_REQ_SERIAL_NUMBER,
    HTTP_REQS,
    NUMBERS,
    SELECTORS,
    SENSORS,
    SLEEP_TIME_AFTER_SET_REQ,
    Factor,
    HotWaterReqState,
    OperatingState,
    PumpState,
    RemkoNumberDef,
    RemkoSelectDef,
    RemkoSensorDef,
    RoomClimateMode,
)


def test_constants() -> None:
    """Test integration constants."""
    assert CONF_HOST == "host"
    assert CONF_SCAN_INTERVAL == "scan_interval"
    assert DOMAIN == "remko_http"
    assert DEFAULT_SCAN_INTERVAL == 20
    assert SLEEP_TIME_AFTER_SET_REQ == 0.4
    assert HTTP_REQ_SERIAL_NUMBER == 5700


@pytest.mark.parametrize(
    ("factor", "value"),
    [
        (Factor.TEMP, 0.1),
        (Factor.POWER, 100),
        (Factor.POWER_KWH, 0.001),
    ],
)
def test_factor(factor: Factor, value: float) -> None:
    """Test conversion factors."""
    assert factor.value == value
    assert float(factor) == value


@pytest.mark.parametrize(
    ("mode", "hex_value"),
    [
        (RoomClimateMode.AUTO, "01"),
        (RoomClimateMode.HEATING, "02"),
        (RoomClimateMode.STANDBY, "03"),
        (RoomClimateMode.COOLING, "04"),
    ],
)
def test_room_climate_mode_hex_value(mode: RoomClimateMode, hex_value: str) -> None:
    """Test room climate mode to hexadecimal conversion."""
    assert mode.hex_value == hex_value


@pytest.mark.parametrize(
    ("hex_value", "mode"),
    [
        ("01", RoomClimateMode.AUTO),
        ("02", RoomClimateMode.HEATING),
        ("03", RoomClimateMode.STANDBY),
        ("04", RoomClimateMode.COOLING),
    ],
)
def test_room_climate_mode_from_hex(hex_value: str, mode: RoomClimateMode) -> None:
    """Test hexadecimal to room climate mode conversion."""
    assert RoomClimateMode.from_hex(hex_value) is mode


def test_room_climate_mode_from_hex_invalid() -> None:
    """Test invalid room climate mode hexadecimal value."""
    assert RoomClimateMode.from_hex("FF") == "Status N/A: FF"


@pytest.mark.parametrize(
    ("state", "hex_value"),
    [
        (HotWaterReqState.STANDBY, "00"),
        (HotWaterReqState.ACTIVE, "01"),
    ],
)
def test_hot_water_req_state_hex_value(state: HotWaterReqState, hex_value: str) -> None:
    """Test hot water request state to hexadecimal conversion."""
    assert state.hex_value == hex_value


@pytest.mark.parametrize(
    ("hex_value", "state"),
    [
        ("00", HotWaterReqState.STANDBY),
        ("01", HotWaterReqState.ACTIVE),
    ],
)
def test_hot_water_req_state_from_hex(hex_value: str, state: HotWaterReqState) -> None:
    """Test hexadecimal to hot water request state conversion."""
    assert HotWaterReqState.from_hex(hex_value) is state


def test_hot_water_req_state_from_hex_invalid() -> None:
    """Test invalid hot water request state hexadecimal value."""
    assert HotWaterReqState.from_hex("FF") == "Status N/A: FF"


@pytest.mark.parametrize(
    ("state", "hex_value"),
    [
        (PumpState.OFF, "00"),
        (PumpState.ON, "01"),
    ],
)
def test_pump_state_hex_value(state: PumpState, hex_value: str) -> None:
    """Test pump state to hexadecimal conversion."""
    assert state.hex_value == hex_value


@pytest.mark.parametrize(
    ("hex_value", "state"),
    [
        ("00", PumpState.OFF),
        ("01", PumpState.ON),
    ],
)
def test_pump_state_from_hex(hex_value: str, state: PumpState) -> None:
    """Test hexadecimal to pump state conversion."""
    assert PumpState.from_hex(hex_value) is state


def test_pump_state_from_hex_invalid() -> None:
    """Test invalid pump state hexadecimal value."""
    assert PumpState.from_hex("FF") == "Status N/A: FF"


@pytest.mark.parametrize(
    ("state", "hex_value"),
    [
        (OperatingState.UNKNOWN, "00"),
        (OperatingState.FAULT, "01"),
        (OperatingState.DEFROST, "02"),
        (OperatingState.DEFROSTBUFFER, "03"),
        (OperatingState.DHWBUFFER, "04"),
        (OperatingState.ENERGYSTORAGE, "05"),
        (OperatingState.HEATING, "06"),
        (OperatingState.COOLING, "07"),
        (OperatingState.CIRCULATION, "09"),
        (OperatingState.STANDBY, "0A"),
        (OperatingState.FROSTPROTECT, "0C"),
        (OperatingState.READY, "40"),
    ],
)
def test_operating_state_hex_value(state: OperatingState, hex_value: str) -> None:
    """Test operating state to hexadecimal conversion."""
    assert state.hex_value == hex_value


@pytest.mark.parametrize(
    ("hex_value", "state"),
    [
        ("00", OperatingState.UNKNOWN),
        ("01", OperatingState.FAULT),
        ("02", OperatingState.DEFROST),
        ("03", OperatingState.DEFROSTBUFFER),
        ("04", OperatingState.DHWBUFFER),
        ("05", OperatingState.ENERGYSTORAGE),
        ("06", OperatingState.HEATING),
        ("07", OperatingState.COOLING),
        ("09", OperatingState.CIRCULATION),
        ("0A", OperatingState.STANDBY),
        ("0C", OperatingState.FROSTPROTECT),
        ("40", OperatingState.READY),
    ],
)
def test_operating_state_from_hex(hex_value: str, state: OperatingState) -> None:
    """Test hexadecimal to operating state conversion."""
    assert OperatingState.from_hex(hex_value) is state


def test_operating_state_from_hex_invalid() -> None:
    """Test invalid operating state hexadecimal value."""
    assert OperatingState.from_hex("FF") == "Status N/A: FF"


def test_selectors() -> None:
    """Test select definitions."""
    assert len(SELECTORS) == 1

    definition = SELECTORS[0]

    assert isinstance(definition, RemkoSelectDef)
    assert definition.key == "set_room_climate_mode"
    assert definition.read_key == "room_climate_mode"
    assert definition.icon == "mdi:home"
    assert definition.http_req == 1088
    assert definition.option == RoomClimateMode


def test_numbers() -> None:
    """Test number definitions."""
    assert len(NUMBERS) == 2

    cold_hotter = NUMBERS[0]
    assert isinstance(cold_hotter, RemkoNumberDef)
    assert cold_hotter.key == "set_cold_hotter"
    assert cold_hotter.read_key == "cold_hotter_state"
    assert cold_hotter.min_value == 0
    assert cold_hotter.max_value == 3
    assert cold_hotter.step == 0.5
    assert cold_hotter.http_req == 1946

    water_temp = NUMBERS[1]
    assert isinstance(water_temp, RemkoNumberDef)
    assert water_temp.key == "set_water_temp_req"
    assert water_temp.read_key == "water_temp_req"
    assert water_temp.min_value == 35
    assert water_temp.max_value == 80
    assert water_temp.step == 0.5
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

    operating_status = next(
        sensor for sensor in SENSORS if sensor.key == "operating_status"
    )

    assert operating_status.device_class == "enum"
    assert operating_status.entity_category == "diagnostic"
    assert operating_status.http_req == 5001
    assert operating_status.option == OperatingState


def test_http_requests_are_unique() -> None:
    """Test that HTTP request IDs are unique."""
    assert len(HTTP_REQS) == len(set(HTTP_REQS))


def test_http_requests_contain_all_definitions() -> None:
    """Test that all configured HTTP requests are collected."""
    expected = {
        definition.http_req
        for definition in (*SELECTORS, *SENSORS, *NUMBERS)
        if definition.http_req is not None
    }

    assert set(HTTP_REQS) == expected
