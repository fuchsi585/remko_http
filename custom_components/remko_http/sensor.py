"""Remko Sensor integration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    ENERGY_SENSORS,
    ENERGY_SENSORS_DEVICE_RAW,
    SENSORS,
    RemkoEnergySensorDef,
    RemkoSensorDef,
)
from .coordinator import DeviceValue, RemkoCoordinator
from .entity import RemkoBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RemkoCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []

    for definition in (
        *SENSORS,
        *ENERGY_SENSORS,
        *ENERGY_SENSORS_DEVICE_RAW,
    ):
        entities.append(RemkoSensor(coordinator, definition, entry))

    async_add_entities(entities)


class RemkoSensor(RemkoBaseEntity, SensorEntity):
    def __init__(
        self,
        coordinator: RemkoCoordinator,
        definition: RemkoSensorDef | RemkoEnergySensorDef,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry, definition)

        self._last_value: float | int | str | None = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        new_value = self.native_value
        if new_value != self._last_value:
            self._last_value = new_value
            self.async_write_ha_state()

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return self._last_value

        value: DeviceValue | None = self.coordinator.data.get(
            self._definition.key, None
        )
        if value is None or value.phys_value is None:
            return self._last_value

        return self._round_value(value.phys_value)

    def _round_value(self, value: float | int | str) -> float | int | str:
        """Round numeric values based on suggested_display_precision."""
        precision = self._definition.display_precision
        if precision is None or not isinstance(value, (int, float)):
            return value
        return round(value, precision) if precision > 0 else int(round(value, 0))
