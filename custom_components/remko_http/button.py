"""Remko Button integration."""

from __future__ import annotations

import asyncio
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    BUTTONS,
    DOMAIN,
    RemkoButtonDef,
)
from .coordinator import RemkoCoordinator
from .entity import RemkoBaseEntity
from .remko_enums import DeviceValue, SwitchState

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Remko selectors from a config entry."""
    coordinator: RemkoCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[RemkoButtonEntity] = []

    for definition in BUTTONS:
        entities.append(RemkoButtonEntity(coordinator, definition, entry))

    async_add_entities(entities)


class RemkoButtonEntity(RemkoBaseEntity, ButtonEntity):
    """An Renko button entity."""

    def __init__(
        self,
        coordinator: RemkoCoordinator,
        definition: RemkoButtonDef,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, entry, definition)
        self._pressed_value = SwitchState.ON
        self._reset_value = SwitchState.OFF

    @property
    def available(self) -> bool:
        if self.coordinator.data is not None:
            value: DeviceValue = self.coordinator.data.get(self._definition.enable_key)
            active = value.phys_value == self._definition.enable_value
        else:
            active = True
        return super().available and active

    async def async_press(self) -> None:
        """Handle button press by sending action command"""
        _LOGGER.debug("Button pressed: %s", self._definition.key)
        await self.coordinator.async_write_to_pump(
            self._definition, self._pressed_value
        )
        if self._definition.reset_delay is not None:
            await asyncio.sleep(self._definition.reset_delay)
            await self.coordinator.async_write_to_pump(
                self._definition, self._reset_value
            )
