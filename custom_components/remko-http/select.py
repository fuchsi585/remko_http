"""Number platform for Remko."""

from __future__ import annotations

import logging
import asyncio

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SELECTORS,
    STATE_MAPPING,
    SLEEP_TIME_AFTER_SET_REQ,
    RemkoSelectDef,
)
from .coordinator import RemkoCoordinator, DeviceValue


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Remko selectors from a config entry."""
    coordinator: RemkoCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[RemkoSelect] = []

    for definition in SELECTORS:
        entities.append(RemkoSelect(coordinator, definition, entry))

    async_add_entities(entities)


class RemkoSelect(CoordinatorEntity[RemkoCoordinator], SelectEntity):
    """An Renko number entity."""

    _attr_available = True
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: RemkoCoordinator, definition: RemkoSelectDef, entry
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._definition = definition
        self._attr_name = definition.name
        self._attr_unique_id = f"{entry.entry_id}_{definition.key}"
        self._attr_translation_key = definition.key
        self._attr_icon = definition.icon
        self._last_written_value: str | None = None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Remko Wärmepumpe",
            manufacturer="Remko",
            model="WKF120",
        )
        self._attr_options = list(
            STATE_MAPPING.get(self._definition.http_req, {}).values()
        )
        self._attr_current_option = self.native_value

    @property
    def byte_size(self):
        return len(self.coordinator.data.get(self._definition.state_key).raw_value)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info from coordinator."""
        return self._attr_device_info

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
            self._definition.state_key, None
        )
        if mapped_name is None:
            return None

        return mapped_name.phys_value

    def _get_selected_hex_value(self, selected_value: str) -> str | None:
        """Return hex-value of selected option."""
        mapping = STATE_MAPPING.get(self._definition.http_req, {})
        for hex_value, mapped_name in mapping.items():
            if mapped_name == selected_value:
                return hex_value

        return None

    async def async_select_option(self, option: str) -> None:
        """Select a new option and write it to the device via HTTP."""
        selected_hex_value = self._get_selected_hex_value(option)

        if selected_hex_value is None:
            return None

        _LOGGER.debug(
            f"Set value for {self._definition.http_req} with '{option}'. HEX-Value: {selected_hex_value}"
        )
        await self.coordinator.async_set_value(
            self._definition.http_req, selected_hex_value
        )
        await asyncio.sleep(SLEEP_TIME_AFTER_SET_REQ)
        await self.coordinator.async_refresh()
