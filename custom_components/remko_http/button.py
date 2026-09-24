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
from .remko_enums import SwitchState

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Remko buttons from a config entry."""
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
        """Initialize the button entity."""
        super().__init__(coordinator, entry, definition)

    @property
    def available(self) -> bool:
        if not super().available or self.coordinator.data is None:
            return False

        availability = getattr(self._definition, "availability", None)
        if availability is not None:
            try:
                return availability(self.coordinator.data)
            except (ValueError, KeyError):
                # Fehlender Messwert kann sonst die Button-Anzeige stören
                return False

        return True

    async def async_press(self) -> None:
        """Handle button press by sending action command"""
        _LOGGER.debug("Button pressed: %s", self._definition.key)
        await self.coordinator.async_write_to_pump(self._definition, SwitchState.ON)
        if self._definition.reset_delay is not None:
            await asyncio.sleep(self._definition.reset_delay)
            await self.coordinator.async_write_to_pump(
                self._definition, SwitchState.OFF
            )
        await self.coordinator.async_request_refresh()
