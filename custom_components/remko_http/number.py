"""Remko Number integration."""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    NUMBERS,
    RemkoNumberDef,
)
from .coordinator import RemkoCoordinator
from .entity import RemkoBaseEntity
from .remko_enums import DeviceValue

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Remko numbers from a config entry."""
    coordinator: RemkoCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[RemkoNumber] = []

    for definition in NUMBERS:
        entities.append(RemkoNumber(coordinator, definition, entry))

    async_add_entities(entities)


class RemkoNumber(RemkoBaseEntity, NumberEntity):
    """An Remko number entity."""

    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: RemkoCoordinator,
        definition: RemkoNumberDef,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, entry, definition)
        self._attr_native_min_value = self._definition.min_value
        self._attr_native_max_value = self._definition.max_value
        self._attr_native_step = self._definition.step
        self._attr_native_value: float | None = None

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        value: DeviceValue | None = (self.coordinator.data or {}).get(
            self._definition.read_key, None
        )
        if value is None:
            return None

        return value.phys_value

    async def async_set_native_value(self, value: float) -> None:
        """Send a new value and write it to the device via HTTP."""
        value = max(self._definition.min_value, min(self._definition.max_value, value))

        _LOGGER.debug(f"Write value for {self._definition.read_key} with '{value}'.")
        await self.coordinator.async_write_to_pump(self._definition, value)
