"""Tests for the Remko coordinator."""

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


def test_energy_calculation_uses_stored_energy_when_available() -> None:
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


def test_energy_calculation_integrates_power_with_trapezoid() -> None:
    """Test power is integrated with the trapezoidal rule."""
    coordinator = _coordinator()
    timestamp = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
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
        {"power": DeviceValue("power", phys_value=200)},
        timestamp + timedelta(seconds=20),
    )

    expected = 10.0 + ((100 + 200) / 2) * (20 / 3600) / 1000
    assert result["energy_electrical"].phys_value == pytest.approx(expected)


def test_energy_calculation_skips_large_time_gap() -> None:
    """Test a large polling gap does not create a false energy spike."""
    coordinator = _coordinator()
    timestamp = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
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
