"""Tests for coordinator-backed REMKO entity state."""

from types import SimpleNamespace

import pytest

from custom_components.remko_http.button import RemkoButtonEntity
from custom_components.remko_http.const import BUTTONS, NUMBERS, SELECTORS, SENSORS
from custom_components.remko_http.number import RemkoNumber
from custom_components.remko_http.remko_enums import DeviceValue, HotWaterReqState
from custom_components.remko_http.select import RemkoSelectEntity
from custom_components.remko_http.sensor import RemkoSensor


@pytest.mark.parametrize(
    ("entity_class", "definition"),
    [
        (RemkoSensor, SENSORS[0]),
        (RemkoNumber, NUMBERS[0]),
        (RemkoSelectEntity, SELECTORS[0]),
    ],
    ids=["sensor", "number", "select"],
)
def test_entity_availability_requires_successful_update_and_value(
    entity_class, definition
) -> None:
    """Availability follows the coordinator and this entity's own value."""
    key = getattr(definition, "read_key", definition.key)
    coordinator = SimpleNamespace(
        data={key: DeviceValue(key, 0)},
        last_update_success=True,
    )
    entry = SimpleNamespace(entry_id="remko", data={})
    entity = entity_class(coordinator, definition, entry)

    assert entity.available is True

    coordinator.last_update_success = False
    assert entity.available is False

    coordinator.last_update_success = True
    coordinator.data = {}
    assert entity.available is False

    coordinator.data = {key: DeviceValue(key, None)}
    assert entity.available is False

    coordinator.data = None
    assert entity.available is False


@pytest.mark.parametrize(
    ("entity_class", "definition"),
    [(RemkoSensor, SENSORS[0]), (RemkoNumber, NUMBERS[0])],
    ids=["sensor", "number"],
)
def test_numeric_entity_returns_none_when_current_value_is_missing(
    entity_class, definition
) -> None:
    """Entities do not expose a stale value when the latest value is absent."""
    key = getattr(definition, "read_key", definition.key)
    coordinator = SimpleNamespace(
        data={key: DeviceValue(key, 12.5)}, last_update_success=True
    )
    entity = entity_class(
        coordinator, definition, SimpleNamespace(entry_id="remko", data={})
    )

    assert entity.native_value is not None

    coordinator.data = {}
    assert entity.native_value is None

    coordinator.data = None
    assert entity.native_value is None


@pytest.mark.parametrize(
    ("target_temperature", "actual_temperature", "request_state", "expected"),
    [
        (50.0, 40.0, HotWaterReqState.STANDBY, True),
        (50.0, 50.0, HotWaterReqState.STANDBY, False),
        (50.0, 60.0, HotWaterReqState.STANDBY, False),
        (50.0, 40.0, HotWaterReqState.ACTIVE, False),
        (None, 40.0, HotWaterReqState.STANDBY, False),
        (50.0, None, HotWaterReqState.STANDBY, False),
        (50.0, 40.0, None, False),
    ],
)
def test_heat_warm_water_button_availability(
    target_temperature, actual_temperature, request_state, expected
) -> None:
    """DHW boost is available only for a cold tank with no active request."""
    coordinator = SimpleNamespace(
        data={
            "action_heat_warm_water": DeviceValue("action_heat_warm_water", 0),
            "water_temp_req": DeviceValue("water_temp_req", target_temperature),
            "water_temp": DeviceValue("water_temp", actual_temperature),
            "hot_water_req_state": DeviceValue("hot_water_req_state", request_state),
        },
        last_update_success=True,
    )
    entity = RemkoButtonEntity(
        coordinator,
        BUTTONS[0],
        SimpleNamespace(entry_id="remko", data={}),
    )

    assert entity.available is expected

    coordinator.last_update_success = False
    assert entity.available is False

    coordinator.data = None
    assert entity.available is False
