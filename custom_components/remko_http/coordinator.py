"""DataUpdateCoordinator for Remk Heatpump."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, replace
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import dt
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ENERGY_SENSORS,
    ENERGY_SENSORS_DEVICE_RAW,
    HTTP_REQS,
    SENSORS,
    RemkoNumberDef,
    RemkoSelectDef,
    RemkoSensorDef,
)
from .remko_enums import decode
from .remkoclient import RemkoHttpClient

_LOGGER = logging.getLogger(__name__)


@dataclass
class DeviceValue:
    key: str
    phys_value: int | float | str | None = None
    raw_value: str | None = None


class RemkoCoordinator(DataUpdateCoordinator):
    """Fetches data from Remko via HTTP request."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        self._client = None
        self._polling = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=self._polling),
        )

        self._firmware: str = ""
        self._serial_number: str = ""
        self._last_data: dict[str, DeviceValue] | None = None
        self._last_time: float = None

    @property
    def firmware(self):
        return self._firmware

    @property
    def serial_number(self):
        return self._serial_number

    async def async_client_shutdown(self) -> None:
        await super().async_shutdown()

    async def async_setup_client(self):
        self._client = RemkoHttpClient(self.config_entry.data.get(CONF_HOST))
        await self._client.async_setup_client(self.hass)

        self._serial_number = await self._client.async_get_serial_number()
        self._firmware = await self._client.async_get_firmware()

    async def async_get_data(self) -> dict[str, Any]:
        data: dict = {}

        raw_data = await self._client.async_get_pump_data(HTTP_REQS)
        for sensor_definition in (*SENSORS, *ENERGY_SENSORS_DEVICE_RAW):
            if hex_value := raw_data.get(sensor_definition.http_req):
                entity_value = DeviceValue(sensor_definition.key)
                entity_value.raw_value = hex_value
                if sensor_definition.option:
                    entity_value.phys_value = sensor_definition.option.from_hex(
                        hex_value
                    )
                    data[entity_value.key] = entity_value
                    continue

                entity_value.phys_value = (
                    decode(hex_value, sensor_definition.data_type)
                    * sensor_definition.scale_type.scale
                )
                data[entity_value.key] = entity_value

        return dict(data)

    def energy_calculation(self, data: dict[str, DeviceValue]) -> dict[str, Any]:
        result: dict[str, DeviceValue] = dict(data)

        for sensor_definition in ENERGY_SENSORS:
            if not sensor_definition.is_calculated:
                continue

            if (
                self._last_data is None
                or self._last_data.get(sensor_definition.key) is None
            ):
                device_value
                if device_value := result.get(f"{sensor_definition.key}_raw"):
                    result[sensor_definition.key] = replace(
                        device_value, key=device_value.key.removesuffix("_raw")
                    )
                continue

            if (last_power := self._last_data.get("power")) is None or (
                current_power := result.get("power")
            ) is None:
                return dict(result)

            now = time.monotonic()
            # Zeitdifferenz in Stunden berechnen
            timediff_hours = (now - self._last_time) / 3_600

            # Berechnung: (Watt * Stunden) / 1000 = kWh
            # Trapezregel
            if current_power.phys_value is not None and timediff_hours > 0:
                additional_energy = (
                    (last_power.phys_value + current_power.phys_value)
                    / 2
                    * timediff_hours
                    / 1_000
                )
                new_energy = self._last_data.get(sensor_definition.key)
                # new_energy.raw_value =
                new_energy.phys_value += round(additional_energy, 2)
                result[sensor_definition.key] = new_energy

        return dict(result)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            result = await self.async_get_data()
            result = self.energy_calculation(result)

            self._last_time = time.monotonic()
            self._last_data = dict(result)

            return dict(result)
        except Exception as err:
            raise UpdateFailed(
                "Remko update failed! Retry in 120 seconds.", retry_after=120
            ) from err

    async def async_set_value(
        self,
        sensor_definition: RemkoSelectDef | RemkoNumberDef | RemkoSensorDef,
        value: str,
    ) -> str:
        if sensor_definition.option:
            values = {
                str(sensor_definition.http_req): sensor_definition.option(
                    value
                ).hex_value
            }
        else:
            values = {str(sensor_definition.http_req): value}

        try:
            response = await self._client.async_set_pump_data(
                sensor_definition.http_req, values
            )
        except Exception:
            _LOGGER.error(
                f"Request for {self._url} of ID {sensor_definition.http_req} with {values}"
            )
            return None

        return response.get(str(sensor_definition.http_req))
