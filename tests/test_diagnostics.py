"""Tests for on-demand REMKO diagnostics."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.remko_http.diagnostics import (
    _async_get_return_temperature_diagnostics,
)


@pytest.mark.asyncio
async def test_return_temperature_diagnostics_isolate_unsupported_signals() -> None:
    """Missing or malformed IDs must not prevent decoding the other candidates."""
    coordinator = MagicMock()
    coordinator._async_real_all_raw_pump_data = AsyncMock(
        side_effect=[
            {5581: "012C"},
            None,
            {5487: "FFF6"},
            {5471: "invalid"},
            {5476: "0001FF"},
        ]
    )

    result = await _async_get_return_temperature_diagnostics(coordinator)

    assert result["5581"] == {
        "label": "Rücklauftemp.",
        "raw_value": "012C",
        "temperature_c": 30.0,
        "status": "decoded",
    }
    assert result["5609"]["status"] == "unavailable"
    assert result["5609"]["temperature_c"] is None
    assert result["5487"]["temperature_c"] == -1.0
    assert result["5471"]["status"] == "invalid_response"
    assert result["5476"]["status"] == "invalid_response"
    assert result["5476"]["raw_value"] == "0001FF"
    assert [
        call.args[0]
        for call in coordinator._async_real_all_raw_pump_data.call_args_list
    ] == [[5581], [5609], [5487], [5471], [5476]]
