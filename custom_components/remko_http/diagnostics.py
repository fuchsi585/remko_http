"""Diagnostics support for Remko HTTP."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, DOMAIN
from .coordinator import RemkoCoordinator

TO_REDACT = (CONF_HOST, "title", "unique_id", "serial_number")


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: RemkoCoordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})

    return async_redact_data(
        {"entry": entry.as_dict(), "domain": DOMAIN, **coordinator.device_info},
        TO_REDACT,
    )
