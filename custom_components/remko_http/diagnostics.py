"""Diagnostics support for Remko HTTP."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, DOMAIN
from .coordinator import RemkoCoordinator
from .remko_enums import RemkoDataType
from .utils import decode

TO_REDACT = (CONF_HOST, "title", "unique_id", "serial_number")


async def _async_get_return_temperature_diagnostics(
    coordinator: RemkoCoordinator,
) -> dict[str, Any]:
    """Read candidate temperatures on demand, independently of normal polling."""
    signals = {
        5581: "Rücklauftemp.",
        5609: "Wasser Eintrittstemperatur",
        5487: "Wasser Eintrittstemperatur",
        5471: "Rücklauftemp.",
        5476: "Rücklauftemp. gemischt",
        5485: "Wasser Austrittstemperatur",
        5339: "Wasser Eintrittstemperatur",
    }
    result = {}
    for signal_id, label in signals.items():
        # Isolate requests so an unsupported ID cannot hide the other values.
        response = await coordinator._async_real_all_raw_pump_data([signal_id])
        raw = response.get(signal_id) if response is not None else None
        signal = {"label": label, "raw_value": raw, "temperature_c": None}
        if raw is None:
            signal["status"] = "unavailable"
        else:
            try:
                signal["temperature_c"] = round(
                    decode(raw, RemkoDataType.INT16) * 0.1, 1
                )
                signal["status"] = "decoded"
            except (ValueError, TypeError):
                signal["status"] = "invalid_response"
        result[str(signal_id)] = signal
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
            "return_temperature_signals": (
                await _async_get_return_temperature_diagnostics(coordinator)
            ),
        },
        TO_REDACT,
    )
