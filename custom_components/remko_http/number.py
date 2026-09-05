"""Number platform for Remko."""

from __future__ import annotations

import asyncio
import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    NUMBERS,
    SLEEP_TIME_AFTER_SET_REQ,
    Factor,
    RemkoNumberDef,
)
from .coordinator import DeviceValue, RemkoCoordinator
from .entity import RemkoBaseEntity

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
        self._last_value: float | None = None

    @property
    def response_size(self):
        return len(self.coordinator.data.get(self._definition.read_key).raw_value)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        new_value = self.native_value
        if new_value != self._last_value:
            self._last_value = new_value
            self.async_write_ha_state()

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        value: DeviceValue = self.coordinator.data.get(self._definition.read_key, None)
        if value is None:
            return None

        return value.phys_value

    @staticmethod
    def _round_number(value: float) -> float:
        return round(value * 2) / 2

    async def async_set_native_value(self, value: float) -> None:
        """Send a new value and write it to the device via HTTP."""
        value = max(
            self._attr_native_min_value, min(self._attr_native_max_value, value)
        )
        rounded_value = (
            int(self._round_number(value) / Factor.TEMP)
            if self._definition.device_class == "temperature"
            else int(self._round_number(value))
        )
        # würde auch hex(rounded_value)[2:].zfill(self._definition.byte_len) gehen
        hex_value = f"%0{self.response_size}X" % rounded_value

        _LOGGER.debug(
            f"Set value for {self._definition.http_req} with '{value}'. HEX-Value: {hex_value}"
        )
        await self.coordinator.async_set_value(self._definition, hex_value)
        await asyncio.sleep(SLEEP_TIME_AFTER_SET_REQ)
        await self.coordinator.async_refresh()
