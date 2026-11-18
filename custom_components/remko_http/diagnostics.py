"""Diagnostics support for Remko HTTP."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_DIAGNOSTIC_IDS, CONF_HOST, DOMAIN
from .coordinator import RemkoCoordinator

TO_REDACT = (CONF_HOST, "title", "unique_id", "serial_number")


def _validate_diagnostic_ids(ids: str) -> dict[str, tuple[int, ...]]:
    result = []
    ids = ids.split(",")

    for id in ids:
        try:
            result.append(int(id.strip()))
        except ValueError:
            continue

    return tuple(result)


async def _async_get_return_diagnostic_ids(
    coordinator: RemkoCoordinator,
    entry: ConfigEntry,
) -> dict[str, Any]:
    result = {}

    ids = _validate_diagnostic_ids(entry.data.get(CONF_DIAGNOSTIC_IDS, ""))
    if not ids:
        return result

    response = await coordinator._async_real_all_raw_pump_data(ids)

    for id in ids:
        raw_value = (response or {}).get(id)
        result[str(id)] = raw_value if raw_value is not None else "unavailable"

    return result


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: RemkoCoordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})

    return async_redact_data(
        {
            "entry": entry.as_dict(),
            "domain": DOMAIN,
            **coordinator.device_info,
            "return_diagnostic_ids": (
                await _async_get_return_diagnostic_ids(coordinator, entry)
            ),
        },
        TO_REDACT,
    )
