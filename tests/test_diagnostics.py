"""Tests for on-demand REMKO diagnostics."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.remko_http.const import CONF_DIAGNOSTIC_IDS, DOMAIN
from custom_components.remko_http.diagnostics import (
    _async_get_return_diagnostic_ids,
    async_get_config_entry_diagnostics,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("response", "expected"),
    [
        (
            {5581: "012C", 5487: "FFF6"},
            {"5581": "012C", "5609": "unavailable", "5487": "FFF6"},
        ),
        (None, {"5581": "unavailable", "5609": "unavailable", "5487": "unavailable"}),
    ],
    ids=["partial_response", "no_response"],
)
async def test_diagnostics_export_configured_ids(
    response: dict[int, str] | None, expected: dict[str, str]
) -> None:
    """Export raw values for configured IDs and skip invalid tokens."""
    entry = MagicMock(
        entry_id="remko",
        data={CONF_DIAGNOSTIC_IDS: "5581, 5609, invalid, 5487"},
    )
    entry.as_dict.return_value = {"data": entry.data}
    read_raw_data = AsyncMock(return_value=response)
    coordinator = MagicMock(device_info={}, _async_real_all_raw_pump_data=read_raw_data)
    hass = MagicMock(data={DOMAIN: {entry.entry_id: coordinator}})

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["return_diagnostic_ids"] == expected
    read_raw_data.assert_awaited_once()
    assert list(read_raw_data.await_args.args[0]) == [5581, 5609, 5487]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "entry_data",
    [{}, {CONF_DIAGNOSTIC_IDS: ""}, {CONF_DIAGNOSTIC_IDS: " , invalid, "}],
    ids=["unset", "empty", "invalid"],
)
async def test_diagnostics_skip_read_when_no_ids_are_configured(
    entry_data: dict[str, str],
) -> None:
    """Skip the device request when the setting yields no IDs."""
    entry = MagicMock(data=entry_data)
    read_raw_data = AsyncMock()
    coordinator = MagicMock(_async_real_all_raw_pump_data=read_raw_data)

    assert await _async_get_return_diagnostic_ids(coordinator, entry) == {}
    read_raw_data.assert_not_awaited()
