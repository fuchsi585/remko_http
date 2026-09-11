"""Tests for the Remko coordinator."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.remko_http.coordinator import RemkoCoordinator
from custom_components.remko_http.remko_enums import (
    CoordinatorSnapshot,
    DeviceValue,
    OperatingState,
)


def _coordinator() -> RemkoCoordinator:
    """Return a coordinator instance without running Home Assistant setup."""
    coordinator = object.__new__(RemkoCoordinator)
    coordinator._polling = 20
    coordinator._session = None
    coordinator._url = "http://127.0.0.1/cgi-bin/webapi.cgi"
    coordinator._firmware = None
    coordinator._last_snapshot = None
    coordinator._last_stored_energies = CoordinatorSnapshot({}, None)
    return coordinator


def test_decode_device_values() -> None:
    """Test decoding raw sensor and energy values."""
    coordinator = _coordinator()

    result = coordinator._decode_device_values(
        {
            5039: "00FA",  # water_temp = 25.0 °C
            5320: "0002",  # power = 200 W
            5001: "06",  # operating_status = heating
            5105: "00000064",  # raw energy = 100 kWh
        }
    )

    assert result["water_temp"].phys_value == 25.0
    assert result["water_temp"].raw_value == "00FA"
    assert result["power"].phys_value == 200
    assert result["operating_status"].phys_value is OperatingState.HEATING
    assert result["energy_electrical_raw"].phys_value == 100


def test_decode_device_values_ignores_unknown_values() -> None:
    """Test unknown response IDs are ignored."""
    coordinator = _coordinator()

    result = coordinator._decode_device_values({9999: "0001"})

    assert result == {}


@pytest.mark.asyncio
async def test_async_read_raw_pump_data() -> None:
    """Test successful raw data retrieval and response flattening."""
    coordinator = _coordinator()
    response = MagicMock()
    response.json.return_value = {
        "SMT_VERSION": "4.25",
        "values": {
            "5700": "123456789",
            "5320": "0002",
        },
    }
    response.raise_for_status.return_value = None

    session = MagicMock()
    session.post = AsyncMock(return_value=response)
    coordinator._session = session

    result = await coordinator._async_read_raw_pump_data([5700, 5320])

    assert result == {5700: "123456789", 5320: "0002"}
    assert coordinator._firmware == "4.25"
    session.post.assert_awaited_once_with(
        coordinator._url,
        json={
            "SMT_ID": "0000000000000000",
            "query_list": [5700, 5320],
        },
        timeout=15,
    )


@pytest.mark.asyncio
async def test_async_read_raw_pump_data_without_session() -> None:
    """Test that a missing session returns None."""
    coordinator = _coordinator()

    assert await coordinator._async_read_raw_pump_data([5320]) is None


@pytest.mark.asyncio
async def test_async_read_raw_pump_data_without_queries() -> None:
    """Test that an empty query list returns None."""
    coordinator = _coordinator()
    coordinator._session = MagicMock()

    assert await coordinator._async_read_raw_pump_data([]) is None
    coordinator._session.post.assert_not_called()


@pytest.mark.asyncio
async def test_async_read_raw_pump_data_http_error() -> None:
    """Test HTTP errors are converted to a None result."""
    from custom_components.remko_http.coordinator import HTTPStatusError

    coordinator = _coordinator()
    response = MagicMock()
    response.raise_for_status.side_effect = HTTPStatusError("boom")

    session = MagicMock()
    session.post = AsyncMock(return_value=response)
    coordinator._session = session

    assert await coordinator._async_read_raw_pump_data([5320]) is None


@pytest.mark.asyncio
async def test_async_write_raw_pump_data() -> None:
    """Test successful raw data writing."""
    coordinator = _coordinator()
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"values": {"5320": "0002"}}

    session = MagicMock()
    session.post = AsyncMock(return_value=response)
    coordinator._session = session

    result = await coordinator._async_write_raw_pump_data(
        5320,
        {"5320": "0002"},
    )

    assert result == {"5320": "0002"}
    session.post.assert_awaited_once_with(
        coordinator._url,
        json={
            "SMT_ID": "0000000000000000",
            "query_list": [5320],
            "values": {"5320": "0002"},
        },
        timeout=15,
    )


def test_energy_calculation_initializes_from_raw_energy() -> None:
    """Test the calculated energy sensor is seeded from the device value."""
    coordinator = _coordinator()
    now = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)

    result = coordinator._energy_calculation(
        {
            "energy_electrical_raw": DeviceValue(
                "energy_electrical_raw",
                phys_value=12.5,
                raw_value="0000000C",
            ),
            "power": DeviceValue("power", phys_value=200, raw_value="0002"),
        },
        now,
    )

    assert result["energy_electrical"].key == "energy_electrical"
    assert result["energy_electrical"].phys_value == 12.5
    assert result["energy_electrical"].raw_value is None


def test_energy_calculation_uses_available_stored_energy_negative_energy_diff() -> None:
    """Test a stored energy value is preferred over the raw device counter."""
    coordinator = _coordinator()
    coordinator._last_stored_energies = CoordinatorSnapshot(
        data={
            "energy_electrical": DeviceValue(
                "energy_electrical",
                phys_value=42.0,
            )
        },
        timestamp=datetime(2026, 9, 8, 11, 0, tzinfo=timezone.utc),
    )

    result = coordinator._energy_calculation(
        {
            "energy_electrical_raw": DeviceValue(
                "energy_electrical_raw",
                phys_value=12.5,
            ),
            "power": DeviceValue("power", phys_value=200),
        },
        datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc),
    )

    assert result["energy_electrical"].phys_value == 42.0


def test_energy_calculation_uses_device_value_large_positive_energy_diff() -> None:
    """Initialize from a higher device counter when the stored value is old."""
    coordinator = _coordinator()
    coordinator._last_stored_energies = CoordinatorSnapshot(
        data={
            "energy_electrical": DeviceValue(
                "energy_electrical",
                phys_value=42.0,
            )
        },
        timestamp=datetime(2026, 9, 8, 11, 0, 0, tzinfo=timezone.utc),
    )

    timestamp = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
    assert coordinator._last_snapshot is None

    result = coordinator._energy_calculation(
        {
            "energy_electrical_raw": DeviceValue(
                "energy_electrical_raw",
                phys_value=50.0,
            ),
            "power": DeviceValue("power", phys_value=200),
        },
        timestamp,
    )

    assert result["energy_electrical"].phys_value == 50.0
    assert result["energy_electrical"].key == "energy_electrical"
    assert result["energy_electrical"].raw_value is None


def test_energy_calculation_uses_stored_value_with_lower_device_value() -> None:
    """Test a stored energy value is preferred over the raw device counter."""
    coordinator = _coordinator()
    coordinator._last_stored_energies = CoordinatorSnapshot(
        data={
            "energy_electrical": DeviceValue(
                "energy_electrical",
                phys_value=42.0,
            )
        },
        timestamp=datetime(2026, 9, 8, 11, 0, 0, tzinfo=timezone.utc),
    )

    timestamp = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
    result = coordinator._energy_calculation(
        {
            "energy_electrical_raw": DeviceValue(
                "energy_electrical_raw",
                phys_value=20.0,
            ),
            "power": DeviceValue("power", phys_value=200),
        },
        timestamp + timedelta(seconds=81),
    )

    assert result["energy_electrical"].phys_value == 42.0


def test_energy_calculation_integrates_power_with_trapezoid() -> None:
    """Test power is integrated with the trapezoidal rule."""
    coordinator = _coordinator()
    timestamp = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
    coordinator._last_stored_energies = CoordinatorSnapshot(
        data={
            "energy_electrical": DeviceValue(
                "energy_electrical",
                phys_value=10.0,
            )
        },
        timestamp=datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc),
    )
    coordinator._last_snapshot = CoordinatorSnapshot(
        data={
            "energy_electrical": DeviceValue(
                "energy_electrical",
                phys_value=10.0,
            ),
            "power": DeviceValue("power", phys_value=100),
        },
        timestamp=timestamp,
    )

    result = coordinator._energy_calculation(
        {"power": DeviceValue("power", phys_value=10000)},
        timestamp + timedelta(seconds=20),
    )

    expected = 10.0 + ((100 + 10000) / 2) * (20 / 3600) / 1000
    assert result["energy_electrical"].phys_value == pytest.approx(expected)


def test_energy_calculation_skips_large_time_gap() -> None:
    """Test a large polling gap does not create a false energy spike."""
    coordinator = _coordinator()
    timestamp = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
    coordinator._last_stored_energies = CoordinatorSnapshot(
        data={
            "energy_electrical": DeviceValue(
                "energy_electrical",
                phys_value=10.0,
            )
        },
        timestamp=datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc),
    )
    coordinator._last_snapshot = CoordinatorSnapshot(
        data={
            "energy_electrical": DeviceValue("energy_electrical", phys_value=10.0),
            "power": DeviceValue("power", phys_value=100),
        },
        timestamp=timestamp,
    )

    result = coordinator._energy_calculation(
        {"power": DeviceValue("power", phys_value=200)},
        timestamp + timedelta(seconds=81),
    )
    print(result)
    assert result["energy_electrical"].phys_value == 10.0


def test_energy_calculation_skips_non_positive_time_delta() -> None:
    """Test zero and negative time deltas do not change energy."""
    coordinator = _coordinator()
    timestamp = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
    coordinator._last_stored_energies = CoordinatorSnapshot(
        data={
            "energy_electrical": DeviceValue(
                "energy_electrical",
                phys_value=10.0,
            )
        },
        timestamp=datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc),
    )
    coordinator._last_snapshot = CoordinatorSnapshot(
        data={
            "energy_electrical": DeviceValue("energy_electrical", phys_value=10.0),
            "power": DeviceValue("power", phys_value=100),
        },
        timestamp=timestamp,
    )

    result = coordinator._energy_calculation(
        {"power": DeviceValue("power", phys_value=200)},
        timestamp,
    )

    assert result["energy_electrical"].phys_value == 10.0


def test_energy_calculation_continues_before_first_storage_flush() -> None:
    """Accumulate consecutive power samples even with no persisted energy."""
    coordinator = _coordinator()
    timestamp = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
    data = {
        "energy_electrical_raw": DeviceValue("energy_electrical_raw", 100.0),
        "power": DeviceValue("power", 3600),
    }

    # Keep the device counter unchanged: only integration can increase energy.
    for seconds, expected in ((0, 100.0), (20, 100.02), (40, 100.04)):
        now = timestamp + timedelta(seconds=seconds)
        result = coordinator._energy_calculation(data, now)
        assert result["energy_electrical"].phys_value == pytest.approx(expected)
        coordinator._last_snapshot = CoordinatorSnapshot(result, now)

    assert coordinator._last_stored_energies.data == {}


@pytest.mark.parametrize("stored_is_null", [False, True], ids=["missing", "null"])
@pytest.mark.asyncio
async def test_async_update_saves_first_valid_energy_immediately(
    monkeypatch: pytest.MonkeyPatch, stored_is_null: bool
) -> None:
    """Persist the first valid energy once, before the periodic timer fires."""
    coordinator = _coordinator()
    coordinator.hass = MagicMock()
    coordinator._store = MagicMock()
    coordinator._store.async_save = AsyncMock()
    coordinator._storage_dirty = False
    coordinator._unsub_storage = None
    if stored_is_null:
        coordinator._last_stored_energies = CoordinatorSnapshot(
            {"energy_electrical": DeviceValue("energy_electrical", None)}, None
        )

    coordinator._async_read_raw_pump_data = AsyncMock(
        return_value={5105: "00000064", 5320: "0024"}
    )
    timestamp = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
    now = MagicMock(return_value=timestamp)
    monkeypatch.setattr("custom_components.remko_http.coordinator.dt.now", now)

    # Exercise decoding, calculation and the real storage flush together.
    result = await coordinator._async_update_data()

    assert result["energy_electrical"].phys_value == 100.0
    coordinator._store.async_save.assert_awaited_once_with(
        {
            "timestamp": timestamp.isoformat(),
            "energy_electrical": {
                "key": "energy_electrical",
                "phys_value": 100.0,
                "raw_value": None,
            },
        }
    )
    assert (
        coordinator._last_stored_energies.data["energy_electrical"].phys_value == 100.0
    )
    assert coordinator._storage_dirty is False

    # Later polls accumulate energy but leave persistence to the timer.
    now.return_value = timestamp + timedelta(seconds=20)
    result = await coordinator._async_update_data()

    assert result["energy_electrical"].phys_value == pytest.approx(100.02)
    assert coordinator._store.async_save.await_count == 1
    assert coordinator._storage_dirty is True


@pytest.mark.asyncio
async def test_async_update_preserves_zero_stored_energy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Zero is a valid stored counter, not a reason to reseed or save immediately."""
    coordinator = _coordinator()
    timestamp = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
    coordinator.hass = MagicMock()
    coordinator._store = MagicMock()
    coordinator._store.async_save = AsyncMock()
    coordinator._storage_dirty = False
    coordinator._unsub_storage = None
    coordinator._last_stored_energies = CoordinatorSnapshot(
        {"energy_electrical": DeviceValue("energy_electrical", 0.0)}, timestamp
    )
    coordinator._async_read_raw_pump_data = AsyncMock(
        return_value={5105: "00000064", 5320: "0024"}
    )
    now = MagicMock(return_value=timestamp)
    monkeypatch.setattr("custom_components.remko_http.coordinator.dt.now", now)

    result = await coordinator._async_update_data()
    assert result["energy_electrical"].phys_value == 0.0
    coordinator._store.async_save.assert_not_awaited()

    now.return_value = timestamp + timedelta(seconds=20)
    result = await coordinator._async_update_data()
    assert result["energy_electrical"].phys_value == pytest.approx(0.02)
    coordinator._store.async_save.assert_not_awaited()


@pytest.mark.parametrize("device_is_null", [False, True], ids=["missing", "null"])
def test_energy_calculation_initializes_when_device_energy_arrives(
    device_is_null: bool,
) -> None:
    """Wait for a usable initial counter, then resume normal accumulation."""
    coordinator = _coordinator()
    timestamp = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
    data = {"power": DeviceValue("power", 3600)}
    if device_is_null:
        data["energy_electrical_raw"] = DeviceValue("energy_electrical_raw", None)

    result = coordinator._energy_calculation(data, timestamp)
    assert "energy_electrical" not in result
    coordinator._last_snapshot = CoordinatorSnapshot(result, timestamp)

    data["energy_electrical_raw"] = DeviceValue("energy_electrical_raw", 100.0)
    for seconds, expected in ((20, 100.0), (40, 100.02)):
        now = timestamp + timedelta(seconds=seconds)
        result = coordinator._energy_calculation(data, now)
        assert result["energy_electrical"].phys_value == pytest.approx(expected)
        coordinator._last_snapshot = CoordinatorSnapshot(result, now)


@pytest.mark.parametrize("power_is_null", [False, True], ids=["missing", "null"])
def test_energy_calculation_preserves_energy_through_power_gap(
    power_is_null: bool,
) -> None:
    """Keep energy through a gap and integrate only consecutive valid samples."""
    coordinator = _coordinator()
    timestamp = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
    complete = {
        "energy_electrical_raw": DeviceValue("energy_electrical_raw", 100.0),
        "power": DeviceValue("power", 3600),
    }
    incomplete = {"energy_electrical_raw": DeviceValue("energy_electrical_raw", 100.0)}
    if power_is_null:
        incomplete["power"] = DeviceValue("power", None)

    for seconds, data, expected in (
        (0, complete, 100.0),
        (20, complete, 100.02),
        (40, incomplete, 100.02),
        (60, complete, 100.02),
        (80, complete, 100.04),
    ):
        now = timestamp + timedelta(seconds=seconds)
        result = coordinator._energy_calculation(data, now)
        assert result["energy_electrical"].phys_value == pytest.approx(expected)
        coordinator._last_snapshot = CoordinatorSnapshot(result, now)


@pytest.mark.parametrize("device_is_null", [False, True], ids=["missing", "null"])
def test_energy_calculation_restores_without_device_counter(
    device_is_null: bool,
) -> None:
    """A stored counter remains usable when the device provides only power."""
    coordinator = _coordinator()
    timestamp = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
    coordinator._last_stored_energies = CoordinatorSnapshot(
        {"energy_electrical": DeviceValue("energy_electrical", 42.0)},
        timestamp - timedelta(hours=1),
    )
    data = {"power": DeviceValue("power", 3600)}
    if device_is_null:
        data["energy_electrical_raw"] = DeviceValue("energy_electrical_raw", None)

    for seconds, expected in ((0, 42.0), (20, 42.02)):
        now = timestamp + timedelta(seconds=seconds)
        result = coordinator._energy_calculation(data, now)
        assert result["energy_electrical"].phys_value == pytest.approx(expected)
        coordinator._last_snapshot = CoordinatorSnapshot(result, now)


@pytest.mark.parametrize("source", ["device", "storage", "snapshot"])
def test_energy_calculation_does_not_mutate_inputs(source: str) -> None:
    """Results must not modify or share mutable values with their inputs."""
    coordinator = _coordinator()
    timestamp = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
    data = {
        "energy_electrical_raw": DeviceValue(
            "energy_electrical_raw", 100.0, "00000064"
        ),
        "power": DeviceValue("power", 3600, "0024"),
    }
    if source in ("storage", "snapshot"):
        coordinator._last_stored_energies = CoordinatorSnapshot(
            {"energy_electrical": DeviceValue("energy_electrical", 42.0)}, timestamp
        )
    if source == "snapshot":
        coordinator._last_snapshot = CoordinatorSnapshot(
            {
                "energy_electrical": DeviceValue("energy_electrical", 50.0),
                "power": DeviceValue("power", 3600),
            },
            timestamp - timedelta(seconds=20),
        )

    original_data = deepcopy(data)
    original_stored = deepcopy(coordinator._last_stored_energies)
    original_previous = deepcopy(coordinator._last_snapshot)
    result = coordinator._energy_calculation(data, timestamp)

    expected = {"device": 100.0, "storage": 42.0, "snapshot": 50.02}[source]
    assert result["energy_electrical"].phys_value == pytest.approx(expected)
    assert data == original_data
    assert coordinator._last_stored_energies == original_stored
    assert coordinator._last_snapshot == original_previous

    # A later consumer changing the result must not affect either source.
    result["energy_electrical"].phys_value = -1
    result["power"].phys_value = -1
    result["energy_electrical_raw"].phys_value = -1
    assert data == original_data
    assert coordinator._last_stored_energies == original_stored
    assert coordinator._last_snapshot == original_previous
