"""Tests for coordinator-backed REMKO entity state."""

from types import SimpleNamespace

import pytest

from custom_components.remko_http.button import RemkoButtonEntity
from custom_components.remko_http.const import BUTTONS, NUMBERS, SELECTORS, SENSORS
from custom_components.remko_http.number import RemkoNumber
from custom_components.remko_http.remko_enums import DeviceValue, HotWaterReqState
from custom_components.remko_http.select import RemkoSelectEntity
from custom_components.remko_http.sensor import RemkoSensor


@pytest.fixture
def heat_warm_water_button() -> tuple[SimpleNamespace, RemkoButtonEntity]:
    """Provide a DHW button with healthy data and a 50 °C target."""
    coordinator = SimpleNamespace(
        data={
            "action_heat_warm_water": DeviceValue("action_heat_warm_water", 0),
            "water_temp_req": DeviceValue("water_temp_req", 50.0),
            "water_temp": DeviceValue("water_temp", 49.8),
            "hot_water_req_state": DeviceValue(
                "hot_water_req_state", HotWaterReqState.STANDBY
            ),
        },
        last_update_success=True,
    )
    entity = RemkoButtonEntity(
        coordinator,
        BUTTONS[0],
        SimpleNamespace(entry_id="remko", data={"host": "192.168.1.50"}),
    )
    return coordinator, entity


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
    entry = SimpleNamespace(entry_id="remko", data={"host": "192.168.1.50"})
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
        coordinator,
        definition,
        SimpleNamespace(entry_id="remko", data={"host": "192.168.1.50"}),
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
        (50.0, 49.8, HotWaterReqState.STANDBY, True),
        (50.0, 49.5, HotWaterReqState.STANDBY, True),
        (50.0, 49.8, HotWaterReqState.ACTIVE, False),
        (50.0, 50.0, HotWaterReqState.STANDBY, False),
        (50.0, 60.0, HotWaterReqState.STANDBY, False),
        (50.0, 40.0, HotWaterReqState.ACTIVE, False),
        (None, 40.0, HotWaterReqState.STANDBY, False),
        (50.0, None, HotWaterReqState.STANDBY, False),
        (50.0, 40.0, None, False),
    ],
)
def test_heat_warm_water_button_availability(
    heat_warm_water_button,
    target_temperature,
    actual_temperature,
    request_state,
    expected,
) -> None:
    """Initial availability uses the target directly, without the hysteresis margin."""
    coordinator, entity = heat_warm_water_button
    coordinator.data["water_temp_req"].phys_value = target_temperature
    coordinator.data["water_temp"].phys_value = actual_temperature
    coordinator.data["hot_water_req_state"].phys_value = request_state

    assert entity.available is expected
    assert entity.available is expected

    coordinator.last_update_success = False
    assert entity.available is False

    coordinator.data = None
    assert entity.available is False


def test_heat_warm_water_button_hysteresis(heat_warm_water_button) -> None:
    """Keep the previous availability inside the band on the same button instance."""
    coordinator, entity = heat_warm_water_button

    for actual, expected in [
        (49.8, True),
        (50.0, False),
        (50.1, False),
        (49.8, False),
        (49.6, False),
        (49.5, True),
        (49.4, True),
        (49.8, True),
        (50.0, False),
    ]:
        coordinator.data["water_temp"].phys_value = actual

        assert entity.available is expected, f"Unexpected availability at {actual} °C"
        assert entity.available is expected, "Repeated reads must remain stable"


@pytest.mark.parametrize("request_state", [HotWaterReqState.ACTIVE, None])
def test_heat_warm_water_button_request_resets_availability(
    heat_warm_water_button, request_state
) -> None:
    """A blocked request requires reaching the lower threshold before re-enabling."""
    coordinator, entity = heat_warm_water_button
    assert entity.available is True

    coordinator.data["hot_water_req_state"].phys_value = request_state
    assert entity.available is False

    coordinator.data["hot_water_req_state"].phys_value = HotWaterReqState.STANDBY
    assert entity.available is False
    assert entity.available is False

    coordinator.data["water_temp"].phys_value = 49.5
    assert entity.available is True

    coordinator.data["water_temp"].phys_value = 49.8
    assert entity.available is True


@pytest.mark.parametrize("previous", [True, False])
@pytest.mark.parametrize(
    "interruption",
    ["failed_update", "missing_data", "missing_temperature", "null_temperature"],
)
def test_heat_warm_water_button_preserves_availability_after_data_interruption(
    heat_warm_water_button, previous: bool, interruption: str
) -> None:
    """Temporary data failures must preserve both hysteresis states on recovery."""
    coordinator, entity = heat_warm_water_button
    coordinator.data["water_temp"].phys_value = 49.8 if previous else 50.0
    assert entity.available is previous
    healthy_data = dict(coordinator.data)

    if interruption == "failed_update":
        coordinator.last_update_success = False
    elif interruption == "missing_data":
        coordinator.data = None
    elif interruption == "missing_temperature":
        del coordinator.data["water_temp"]
    else:
        coordinator.data["water_temp"] = DeviceValue("water_temp", None)

    assert entity.available is False
    assert entity.available is False

    coordinator.last_update_success = True
    coordinator.data = healthy_data
    coordinator.data["water_temp"].phys_value = 49.8
    assert entity.available is previous
    assert entity.available is previous


@pytest.mark.parametrize(
    "missing_key",
    ["action_heat_warm_water", "water_temp_req", "water_temp", "hot_water_req_state"],
)
def test_heat_warm_water_button_unavailable_when_dependency_is_missing(
    heat_warm_water_button, missing_key: str
) -> None:
    """A partial device response must not break the button availability check."""
    coordinator, entity = heat_warm_water_button
    del coordinator.data[missing_key]

    assert entity.available is False


@pytest.mark.parametrize(
    ("host", "expected"),
    [("192.168.1.50", "192.168.1.50"), ("2001:0db8::1", "[2001:db8::1]")],
)
def test_entity_configuration_url_uses_normalized_host(
    host: str, expected: str
) -> None:
    """The device link uses the same URL-safe IP format as the CGI client."""
    coordinator = SimpleNamespace(device_info={})
    entry = SimpleNamespace(entry_id="remko", data={"host": host})
    entity = RemkoSensor(coordinator, SENSORS[0], entry)

    assert entity.device_info["configuration_url"] == f"http://{expected}/"
