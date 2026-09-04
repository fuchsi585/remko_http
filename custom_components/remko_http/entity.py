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
    RemkoSwitchDef,
)
from .coordinator import RemkoCoordinator


class RemkoBaseEntity(CoordinatorEntity[RemkoCoordinator]):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RemkoCoordinator,
        entry: ConfigEntry,
        definition: RemkoSwitchDef | RemkoSensorDef | RemkoSelectDef | RemkoNumberDef,
    ) -> None:
        super().__init__(coordinator)
        self._entry_id = entry.entry_id
        self._definition = definition
        # self._attr_name = self._definition.name
        self._attr_unique_id = f"{self._entry_id}_{self._definition.key}"
        self._attr_translation_key = self._definition.key
        self._attr_native_unit_of_measurement = self._definition.unit
        self._attr_icon = self._definition.icon

    @property
    def device_info(self) -> DeviceInfo:
        """Return Home Assistant device info."""
        info = {
            "identifiers": {(DOMAIN, self._entry_id)},
            "translation_key": "heat_pump",
            "manufacturer": "Remko",
            "model": "WKF120",
            # serial_number=coordinator.serial_number,
            "sw_version": self.coordinator.firmware,
        }

        return DeviceInfo(**info)

    @property
    def available(self) -> bool:
        return super().available
