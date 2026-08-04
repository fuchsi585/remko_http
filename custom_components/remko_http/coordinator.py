"""DataUpdateCoordinator for Remk Heatpump."""

from __future__ import annotations

import logging
import time

from dataclasses import dataclass
from typing import Any
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .remkoclient import RemkoHttpClient

from .const import (
    DOMAIN,
    ALL_QUERIES,
    STATE_MAPPING,
    SENSORS,
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    Factor,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class DeviceValue:
    key: str
    phys_value: Any | None = None
    raw_value: str | None = None
    timestamp: float | None = None


# TODO:
# - Add error handling for HTTP client methods, e.g., retries, logging, etc.
# - Consider adding a method to refresh the client session if needed, e.g., in case of connection issues.
# - Implement a method to gracefully shut down the HTTP client session when the coordinator is stopped or removed.
# - Add type hints for all methods and properties for better code clarity and maintainability.
# - Consider adding a method to handle specific pump commands or settings changes, if applicable.
# - Implement a method to validate the configuration entry data, e.g., check if the host is reachable before setting up the client.
# - Add logging for important events, e.g., when the client is set up, when data is fetched, when errors occur, etc.


class RemkoCoordinator(DataUpdateCoordinator):
    """Fetches data from Remko via HTTP request."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        self._hass = hass
        self._entry = entry
        self._client = None
        self._all_queries = ALL_QUERIES
        self._polling = self._entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        super().__init__(
            self._hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=self._polling),
        )

        self._firmware: str = ""
        self._serial_number: str = ""

    @property
    def firmware(self):  # 'SMT_VERSION'
        return self._firmware

    @property
    def serial_number(self):  # '5700'
        return self._serial_number

    async def async_client_shutdown(self) -> None:
        await super().async_shutdown()

    async def async_setup_client(self):
        self._client = RemkoHttpClient(self._entry.data.get(CONF_HOST))
        await self._client.async_setup_client(self._hass)

        self._serial_number = await self._client.async_get_serial_number()
        self._firmware = await self._client.async_get_firmware()

    @staticmethod
    def _hex2number(hex_value: str, factor: Factor) -> float:
        raw = int(hex_value, 16)
        return (raw - 0x10000 if raw > 0x7FFF else raw) * factor

    async def async_fetch_all(self) -> dict:
        data: dict = {}

        raw_data = await self._client.async_get_pump_data(self._all_queries)
        for sensor_def in SENSORS:
            if hex_value := raw_data.get(sensor_def.http_req, None):
                entity_value = DeviceValue(sensor_def.key)
                entity_value.raw_value = hex_value
                entity_value.timestamp = time.monotonic()
                if sensor_def.entity_category == "diagnostic":
                    if mapping_def := STATE_MAPPING.get(sensor_def.http_req, None):
                        entity_value.phys_value = mapping_def.get(
                            hex_value, f"Status N/A: {hex_value}"
                        )
                    else:
                        entity_value.phys_value = "Status N/A"
                elif sensor_def.device_class == "temperature":
                    entity_value.phys_value = round(
                        self._hex2number(hex_value, Factor.TEMP), 1
                    )
                elif sensor_def.device_class == "power":
                    entity_value.phys_value = int(hex_value, 16) * Factor.POWER
                else:
                    entity_value.phys_value = int(hex_value, 16)

                data[entity_value.key] = entity_value

        return data

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            result = await self.async_fetch_all()

            return dict(result)
        except Exception:
            raise UpdateFailed(
                f"Remko update failed! Retry in 120 seconds.", retry_after=120
            )

    async def async_set_value(self, remko_reg: int, value: str) -> str:
        values = {str(remko_reg): value}

        try:
            response = await self._client.async_set_pump_data(remko_reg, values)
        except:
            _LOGGER.error(f"Request for {self._url} of ID {remko_reg} with {values}")
            return None

        return response.get(str(remko_reg), None)
