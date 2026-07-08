"""Number platform for Remko."""

from __future__ import annotations

import logging
import asyncio

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    NUMBERS,
    SLEEP_TIME_AFTER_SET_REQ,
    Factor,
    RemkoNumberDef,
)
from .coordinator import RemkoCoordinator, DeviceValue


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


class RemkoNumber(CoordinatorEntity[RemkoCoordinator], NumberEntity):
    """An Remko number entity."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX

    def __init__(
        self, coordinator: RemkoCoordinator, definition: RemkoNumberDef, entry
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._definition = definition
        self._attr_name = definition.name
        self._attr_unique_id = f"{entry.entry_id}_{definition.key}"
        self._attr_translation_key = definition.key
        self._attr_icon = definition.icon
        self._attr_native_unit_of_measurement = definition.unit
        self._attr_native_min_value = definition.min_value
        self._attr_native_max_value = definition.max_value
        self._attr_native_step = definition.step
        self._attr_native_value: float | None = None

        self._last_written_value: float | None = None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Remko Wärmepumpe",
            manufacturer="Remko",
            model="WKF120",
        )

    @property
    def response_size(self):
        return len(self.coordinator.data.get(self._definition.state_key).raw_value)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info from coordinator."""
        return self._attr_device_info

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        new_value = self.native_value
        if new_value != self._last_written_value:
            self._last_written_value = new_value
            self.async_write_ha_state()

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        value: DeviceValue = self.coordinator.data.get(self._definition.state_key, None)
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
        await self.coordinator.async_set_value(self._definition.http_req, hex_value)
        await asyncio.sleep(SLEEP_TIME_AFTER_SET_REQ)
        await self.coordinator.async_refresh()
