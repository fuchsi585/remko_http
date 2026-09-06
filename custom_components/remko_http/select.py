"""Number platform for Remko."""

from __future__ import annotations

import asyncio
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    SELECTORS,
    SLEEP_TIME_AFTER_SET_REQ,
    RemkoSelectDef,
)
from .coordinator import DeviceValue, RemkoCoordinator
from .entity import RemkoBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Remko selectors from a config entry."""
    coordinator: RemkoCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[RemkoSelectEntity] = []

    for definition in SELECTORS:
        entities.append(RemkoSelectEntity(coordinator, definition, entry))

    async_add_entities(entities)


class RemkoSelectEntity(RemkoBaseEntity, SelectEntity):
    """An Renko number entity."""

    def __init__(
        self,
        coordinator: RemkoCoordinator,
        definition: RemkoSelectDef,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, entry, definition)
        self._last_value: str | None = None
        self._attr_current_option = self.native_value

    @property
    def byte_size(self):
        return len(self.coordinator.data.get(self._definition.read_key).raw_value)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        new_option = self.native_value
        if new_option != self._attr_current_option:
            self._attr_current_option = new_option
            self.async_write_ha_state()

    @property
    def native_value(self) -> int | None:
        """Return the current value."""
        mapped_name: DeviceValue = self.coordinator.data.get(
            self._definition.read_key, None
        )
        if mapped_name is None:
            return None

        return mapped_name.phys_value

    async def async_select_option(self, option: str) -> None:
        """Select a new option and write it to the device via HTTP."""

        _LOGGER.debug(f"Set value for {self._definition.http_req} with '{option}'.")
        await self.coordinator.async_set_value(self._definition, option)
        await asyncio.sleep(SLEEP_TIME_AFTER_SET_REQ)
        await self.coordinator.async_refresh()
