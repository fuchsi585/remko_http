"""Sensor base entity for Remko"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    RemkoNumberDef,
    RemkoSelectDef,
    RemkoSensorDef,
)
from .coordinator import RemkoCoordinator


class RemkoBaseEntity(CoordinatorEntity[RemkoCoordinator]):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RemkoCoordinator,
        entry: ConfigEntry,
        definition: RemkoSensorDef | RemkoSelectDef | RemkoNumberDef,
    ) -> None:
        super().__init__(coordinator)
        self._entry_id = entry.entry_id
        self._definition = definition
        self._attr_unique_id = f"{self._entry_id}_{self._definition.key}"
        self._attr_translation_key = self._definition.key
        self._attr_native_unit_of_measurement = self._definition.unit
        self._attr_icon = self._definition.icon

        if device_class := getattr(self._definition, "device_class", None):
            self._attr_device_class = device_class

        if state_class := getattr(self._definition, "state_class", None):
            self._attr_state_class = state_class

        if entity_category := getattr(self._definition, "entity_category", None):
            self._attr_entity_category = entity_category

        if self._definition.disabled_by_default:
            self._attr_entity_registry_enabled_default = False

        if display_precision := getattr(self._definition, "display_precision", None):
            self._attr_suggested_display_precision = display_precision

        if option := getattr(self._definition, "option", None):
            self._attr_options = list(option)

    @property
    def device_info(self) -> DeviceInfo:
        """Return Home Assistant device info."""
        info = {
            "identifiers": {(DOMAIN, self._entry_id)},
            "translation_key": "heat_pump",
            "manufacturer": "Remko",
            "model": "WKF120",
            "sw_version": self.coordinator.firmware,
        }

        return DeviceInfo(**info)

    @property
    def available(self) -> bool:
        return super().available
