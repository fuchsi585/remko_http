"""Tests for the REMKO config flow."""

from unittest.mock import MagicMock

import pytest

from custom_components.remko_http.config_flow import RemkoHeatPumpConfigFlow


@pytest.mark.asyncio
async def test_config_flow_rejects_second_instance() -> None:
    """Only one REMKO device can be configured."""
    flow = RemkoHeatPumpConfigFlow()
    flow._async_current_entries = MagicMock(return_value=[object()])
    flow.async_abort = MagicMock(return_value={"reason": "single_instance_allowed"})

    result = await flow.async_step_user({"host": "192.168.1.50", "scan_interval": 20})

    assert result == {"reason": "single_instance_allowed"}
    flow.async_abort.assert_called_once_with(reason="single_instance_allowed")


@pytest.mark.asyncio
async def test_config_flow_creates_entry_for_valid_ip() -> None:
    """A valid IP and interval are retained in the new config entry."""
    flow = RemkoHeatPumpConfigFlow()
    flow._async_current_entries = MagicMock(return_value=[])
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
    user_input = {"host": "192.168.1.50", "scan_interval": 30}

    result = await flow.async_step_user(user_input)

    assert result == {"type": "create_entry"}
    flow.async_create_entry.assert_called_once_with(
        title="Remko (192.168.1.50)", data=user_input
    )


@pytest.mark.asyncio
async def test_config_flow_shows_error_for_invalid_ip() -> None:
    """Malformed host input leaves the flow on the form with an error."""
    flow = RemkoHeatPumpConfigFlow()
    flow._async_current_entries = MagicMock(return_value=[])
    flow.async_show_form = MagicMock(return_value={"type": "form"})

    result = await flow.async_step_user({"host": "remko.invalid", "scan_interval": 20})

    assert result == {"type": "form"}
    errors = flow.async_show_form.call_args.kwargs["errors"]
    assert "Wrong IP-Adress" in errors["base"]
