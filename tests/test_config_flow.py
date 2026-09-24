"""Tests for the REMKO config flow."""

from unittest.mock import MagicMock

import pytest

from custom_components.remko_http.config_flow import (
    RemkoHeatPumpConfigFlow,
    RemkoHeatPumpOptionsFlow,
)


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
@pytest.mark.parametrize(
    "host", ["192.168.1.50", "2001:0db8:0000:0000:0000:0000:0000:0001"]
)
async def test_config_flow_creates_entry_for_valid_ip(host: str) -> None:
    """A valid IP and interval are retained in the new config entry."""
    flow = RemkoHeatPumpConfigFlow()
    flow._async_current_entries = MagicMock(return_value=[])
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
    user_input = {"host": host, "scan_interval": 30}
    expected_data = dict(user_input)

    result = await flow.async_step_user(user_input)

    assert result == {"type": "create_entry"}
    flow.async_create_entry.assert_called_once_with(
        title=f"Remko ({host})", data=expected_data
    )
    assert user_input == expected_data


@pytest.mark.asyncio
async def test_config_flow_shows_error_for_invalid_ip() -> None:
    """Malformed host input leaves the flow on the form with an error."""
    flow = RemkoHeatPumpConfigFlow()
    flow._async_current_entries = MagicMock(return_value=[])
    flow.async_show_form = MagicMock(return_value={"type": "form"})

    result = await flow.async_step_user({"host": "remko.invalid", "scan_interval": 20})

    assert result == {"type": "form"}
    errors = flow.async_show_form.call_args.kwargs["errors"]
    assert errors["base"] == "invalid_host"


@pytest.mark.asyncio
@pytest.mark.parametrize("host", ["192.168.1.50", "192.168.1.51", "2001:db8::1"])
async def test_options_flow_returns_mapping_for_storage(host: str) -> None:
    """Saving options must leave an entry that Home Assistant can serialize."""
    entry = MagicMock()
    entry.data = {"host": "192.168.1.50", "scan_interval": 20}
    flow = RemkoHeatPumpOptionsFlow(entry)
    flow.hass = MagicMock()
    flow.async_create_entry = MagicMock(side_effect=lambda **kwargs: kwargs)
    user_input = {"host": host, "scan_interval": 30}

    result = await flow.async_step_init(user_input)

    flow.hass.config_entries.async_update_entry.assert_called_once_with(
        entry, data=user_input
    )
    assert isinstance(result["data"], dict)
    assert dict(result["data"]) == {}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "host", ["remko.invalid", "[2001:db8::1]", "2001:db8::invalid"]
)
async def test_options_flow_rejects_invalid_host(host: str) -> None:
    """Invalid changed hosts must not update the stored entry."""
    entry = MagicMock()
    entry.data = {"host": "192.168.1.50", "scan_interval": 20}
    flow = RemkoHeatPumpOptionsFlow(entry)
    flow.hass = MagicMock()
    flow.async_show_form = MagicMock(return_value={"type": "form"})
    flow.async_create_entry = MagicMock()

    result = await flow.async_step_init({"host": host, "scan_interval": 30})

    assert result == {"type": "form"}
    assert flow.async_show_form.call_args.kwargs["errors"] == {"base": "invalid_host"}
    flow.hass.config_entries.async_update_entry.assert_not_called()
    flow.async_create_entry.assert_not_called()
