"""Tests for Remko HTTP constants and definitions."""

from custom_components.remko_http.const import (
    ALL_QUERIES,
    AVAILABLE_NUMBER_QUERIES,
    AVAILABLE_SELECT_QUERIES,
    AVAILABLE_SENSOR_QUERIES,
    NUMBERS,
    SELECTORS,
    SENSORS,
    STATE_MAPPING,
    Factor,
)


def test_factor_values() -> None:
    """Test conversion factors."""
    assert Factor.TEMP == 0.1
    assert Factor.POWER == 100
    assert Factor.POWER_KWH == 0.001


def test_sensor_keys_are_unique() -> None:
    """Test that all sensor keys are unique."""
    keys = [sensor.key for sensor in SENSORS]

    assert len(keys) == len(set(keys))


def test_sensor_http_requests_are_unique() -> None:
    """Test that all sensor HTTP request IDs are unique."""
    requests = [sensor.http_req for sensor in SENSORS]

    assert len(requests) == len(set(requests))


def test_number_keys_are_unique() -> None:
    """Test that all number keys are unique."""
    keys = [number.key for number in NUMBERS]

    assert len(keys) == len(set(keys))


def test_select_keys_are_unique() -> None:
    """Test that all select keys are unique."""
    keys = [selector.key for selector in SELECTORS]

    assert len(keys) == len(set(keys))


def test_all_sensor_queries_are_available() -> None:
    """Test that all sensor queries are part of ALL_QUERIES."""
    assert set(AVAILABLE_SENSOR_QUERIES) <= set(ALL_QUERIES)


def test_all_number_queries_are_available() -> None:
    """Test that all number queries are part of ALL_QUERIES."""
    assert set(AVAILABLE_NUMBER_QUERIES) <= set(ALL_QUERIES)


def test_all_select_queries_are_available() -> None:
    """Test that all select queries are part of ALL_QUERIES."""
    assert set(AVAILABLE_SELECT_QUERIES) <= set(ALL_QUERIES)


def test_operating_status_mapping() -> None:
    """Test operating status mappings."""
    mapping = STATE_MAPPING[5001]

    assert mapping["00"] == "unknown"
    assert mapping["01"] == "fault"
    assert mapping["02"] == "defrosting"
    assert mapping["06"] == "heating"
    assert mapping["07"] == "cooling"
    assert mapping["0A"] == "standby"
    assert mapping["40"] == "ready"


def test_room_climate_mode_mapping() -> None:
    """Test room climate mode mappings."""
    mapping = STATE_MAPPING[1088]

    assert mapping["01"] == "auto"
    assert mapping["02"] == "heating"
    assert mapping["03"] == "standby"
    assert mapping["04"] == "cooling"


def test_hot_water_mapping() -> None:
    """Test hot water state mappings."""
    mapping = STATE_MAPPING[5064]

    assert mapping["00"] == "standby"
    assert mapping["01"] == "active"


def test_circulation_pump_mapping() -> None:
    """Test circulation pump state mappings."""
    mapping = STATE_MAPPING[5151]

    assert mapping["00"] == "off"
    assert mapping["01"] == "on"
