"""Remko Sensor integration (YAML platform, no discovery)."""

from __future__ import annotations

import time
from dataclasses import dataclass

from homeassistant.components.sensor import (
    EntityCategory,
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSORS, RemkoSensorDef
from .entity import RemkoBaseEntity
from .coordinator import RemkoCoordinator, DeviceValue


@dataclass(frozen=False)
class RemkoSensorDescription(SensorEntityDescription):
    pass


_STATE_CLASS_MAP = {
    "measurement": SensorStateClass.MEASUREMENT,
    "total_increasing": SensorStateClass.TOTAL_INCREASING,
}

_ENTITY_CATEGORY_MAP = {
    "diagnostic": EntityCategory.DIAGNOSTIC,
    "config": EntityCategory.CONFIG,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RemkoCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []

    for definition in SENSORS:
        entities.append(RemkoSensor(coordinator, definition, entry))

    entities.append(RemkoEnergySensor(coordinator, entry))

    async_add_entities(entities)


class RemkoSensor(RemkoBaseEntity, RestoreSensor):
    def __init__(
        self, coordinator: RemkoCoordinator, definition: RemkoSensorDef, entry
    ) -> None:
        super().__init__(coordinator, entry, definition)
        # self._attr_translation_key = definition.name
        self._restored_value: float | int | str | None = None
        self._last_value: float | int | str | None = None

        if definition.device_class:
            self._attr_device_class = SensorDeviceClass(definition.device_class)
        if definition.state_class:
            self._attr_state_class = _STATE_CLASS_MAP.get(definition.state_class)
        if definition.entity_category:
            self._attr_entity_category = _ENTITY_CATEGORY_MAP.get(
                definition.entity_category
            )
        if definition.disabled_by_default:
            self._attr_entity_registry_enabled_default = False
        if definition.display_precision is not None:
            self._attr_suggested_display_precision = definition.display_precision

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        new_value = self.native_value
        if new_value != self._last_value:
            self._last_value = new_value
            self.async_write_ha_state()

    @property
    def native_value(self):
        if self.coordinator.data is not None:
            value: DeviceValue = self.coordinator.data.get(self._definition.key, None)
            if value is not None:
                return self._round_value(value.phys_value)

        return (
            self._last_value if self._last_value is not None else self._restored_value
        )

    def _round_value(self, value: float | int | str) -> float | int | str:
        """Round numeric values based on suggested_display_precision."""
        precision = self._definition.display_precision
        if precision is None or not isinstance(value, (int, float)):
            return value
        return round(value, precision) if precision > 0 else int(round(value, 0))


class RemkoEnergySensor(CoordinatorEntity[RemkoCoordinator], RestoreSensor):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "kWh"
    _attr_has_entity_name = True

    def __init__(self, coordinator: RemkoCoordinator, entry) -> None:
        super().__init__(coordinator)
        self._attr_name = "berechnete Energie"
        self._attr_unique_id = f"{entry.entry_id}_energy_calc"
        self._attr_icon = "mdi:transmission-tower"
        self._last_time = time.monotonic()
        self._state = 0.0  # Total kWh
        self._last_time = None
        self._attr_device_info = DeviceInfo(
            {
                "identifiers": {(DOMAIN, entry.entry_id)},
                "translation_key": "heat_pump",
                "manufacturer": "Remko",
                "model": "WKF120",
                "sw_version": coordinator.firmware,
            }
        )

    async def async_added_to_hass(self) -> None:
        """Wird aufgerufen, wenn die Entität hinzugefügt wird."""
        await super().async_added_to_hass()

        # Den letzten Status aus der Datenbank laden
        if (last_sensor_data := await self.async_get_last_sensor_data()) is not None:
            self._state = last_sensor_data.native_value

        # Erst jetzt den Zeitstempel setzen, damit die Berechnung ab hier startet
        self._last_time = time.monotonic()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Wird aufgerufen, wenn der Coordinator neue Daten hat."""
        # Hol dir die Watt aus den neuen Daten deines Coordinators
        current_power: DeviceValue = self.coordinator.data.get("power", None)
        # now = time.monotonic()  # -> time im coordinator schreiben
        if current_power is None:
            return
        # Falls dies der erste Durchlauf nach Start ist: nur Zeitstempel merken
        if self._last_time is None:
            self._last_time = current_power.timestamp
            return

        # Zeitdifferenz in Stunden berechnen
        timediff_hours = (current_power.timestamp - self._last_time) / 3600

        # Berechnung: (Watt * Stunden) / 1000 = kWh
        if current_power.phys_value is not None and timediff_hours > 0:
            additional_energy = (current_power.phys_value * timediff_hours) / 1000
            self._state += additional_energy
            self._last_time = current_power.timestamp
            self.async_write_ha_state()

    @property
    def native_value(self):
        # Sicherstellen, dass wir nicht None zurückgeben, wenn der State noch lädt
        return round(self._state, 2) if self._state is not None else 0.0
