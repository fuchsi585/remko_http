"""DataUpdateCoordinator for Remk Heatpump."""

from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import dataclass, replace, asdict
from datetime import timedelta, datetime
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.httpx_client import get_async_client
from httpx import HTTPStatusError, InvalidURL, RequestError, AsyncClient

from .const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ENERGY_SENSORS,
    ENERGY_SENSORS_DEVICE_RAW,
    HTTP_REQS,
    HTTP_REQ_SERIAL_NUMBER,
    SENSORS,
    RemkoNumberDef,
    RemkoSelectDef,
    RemkoSensorDef,
)
from .remko_enums import decode

_LOGGER = logging.getLogger(__name__)


@dataclass
class DeviceValue:
    key: str
    phys_value: int | float | str | None = None
    raw_value: str | None = None


@dataclass
class CoordinatorSnapshot:
    data: dict[str, DeviceValue]
    timestamp: datetime | None


HTTP_TIMEOUT = 15
STORAGE_KEYS: tuple[str, ...] = ("energy_electrical",)


class RemkoCoordinator(DataUpdateCoordinator):
    """Fetches data from Remko via HTTP request."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:

        self._polling = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        self._firmware: str = ""
        self._serial_number: str = ""
        self._last_snapshot: CoordinatorSnapshot | None = None
        self._url: str = f"http://{entry.data.get(CONF_HOST)}/cgi-bin/webapi.cgi"
        self._session: AsyncClient | None = None
        self._store: Store[dict[str, Any]] = Store(
            hass, 1, f"{DOMAIN}.{entry.entry_id}.energy_values"
        )
        self._last_stored_energies: CoordinatorSnapshot = CoordinatorSnapshot({}, None)
        # Merker, ob seit dem letzten Save etwas geändert wurde.
        self._storage_dirty = False
        self._unsub_storage = None
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=self._polling),
        )

    @property
    def firmware(self):
        return self._firmware

    @property
    def serial_number(self):
        return self._serial_number

    async def async_load_storage(self) -> None:
        """Seed the state from disk so the first poll is validated."""
        if (stored := await self._store.async_load()) is None:
            return

        timestamp = parse_datetime(stored.get("timestamp"))
        self._last_stored_energies = CoordinatorSnapshot(
            data={
                key: DeviceValue(**values)
                for key, values in stored.items()
                if key != "timestamp"
            },
            timestamp=timestamp,
        )
        _LOGGER.info(
            f"Load last_snapshot of energies at {self._last_stored_energies.timestamp}"
        )

    async def _async_storage_flush(self, _now: datetime) -> None:
        """Persist current values every 10 minutes."""
        if not self._storage_dirty:
            return

        if (snapshot := self._last_snapshot) is None:
            return

        storage_data = {
            "timestamp": snapshot.timestamp.isoformat(),
            **{
                key: asdict(value)
                for key, value in snapshot.data.items()
                if key in STORAGE_KEYS
            },
        }

        await self._store.async_save(storage_data)

        self._last_stored_energies = CoordinatorSnapshot(
            data={
                key: replace(value)
                for key, value in snapshot.data.items()
                if key in STORAGE_KEYS
            },
            timestamp=snapshot.timestamp,
        )

        self._storage_dirty = False
        _LOGGER.info(
            f"Save last_snapshot of energies at {snapshot.timestamp.isoformat()}"
        )

    async def async_client_shutdown(self) -> None:
        if self._unsub_storage is not None:
            self._unsub_storage()
            self._unsub_storage = None

        if self._storage_dirty:
            await self._async_storage_flush(dt.now())

        await super().async_shutdown()

    async def async_setup_client(self):
        if self._session is None:
            self._session = get_async_client(self.hass, verify_ssl=False)

        response = await self._async_get_raw_pump_data([HTTP_REQ_SERIAL_NUMBER])
        self._serial_number = response.get(HTTP_REQ_SERIAL_NUMBER, "unknown")
        self._firmware = response.get("SMT_VERSION", "unknown")

    async def _async_get_raw_pump_data(
        self, queries: list[int]
    ) -> dict[str, str] | None:
        if not queries or not self._session:
            _LOGGER.warning("HttpClient not initialized or queries is empty!")
            return None

        result: dict[str, str] = {}
        payload = {
            "SMT_ID": "0000000000000000",
            "query_list": list(queries),
        }
        try:
            resp = await self._session.post(
                self._url, json=payload, timeout=HTTP_TIMEOUT
            )
            resp.raise_for_status()
            data = resp.json()
            if "values" in data:
                data.update(data.pop("values"))
                for query_id in queries:
                    result[query_id] = data.get(str(query_id))

        except (HTTPStatusError, InvalidURL, RequestError) as err:
            _LOGGER.error(f"Remko-Client error: {repr(err)}")
            return None

        return dict(result)

    async def _async_set_raw_pump_data(
        self, remko_id: int, values: dict
    ) -> dict[str, str] | None:
        payload = {
            "SMT_ID": "0000000000000000",
            "query_list": [remko_id],
            "values": values,
        }
        try:
            response = await self._session.post(
                self._url, json=payload, timeout=HTTP_TIMEOUT
            )
            response.raise_for_status()
        except (HTTPStatusError, InvalidURL, RequestError) as err:
            _LOGGER.error(f"Remko-Client error: {repr(err)}")
            return None

        return response.json()

    def _sanitize_data(self, raw_data: dict[str, str]) -> dict[str, DeviceValue]:
        data: dict = {}
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

        return data

    async def async_energy_calculation(
        self, data: dict[str, DeviceValue], now: datetime
    ) -> dict[str, DeviceValue]:
        # REMKO provides the current accumulated electrical energy via 5105.
        # Use it as the initial value and continue integrating power (5320)
        # because the device counter is not reliable for our use case.
        result: dict[str, DeviceValue] = deepcopy(data)

        for sensor_definition in ENERGY_SENSORS:
            if not sensor_definition.is_calculated:
                continue

            if (
                self._last_snapshot is None
                or self._last_snapshot.data.get(sensor_definition.key) is None
            ):
                if self._last_stored_energies.data.get(sensor_definition.key) is None:
                    if device_value := result.get(f"{sensor_definition.key}_raw"):
                        result[sensor_definition.key] = replace(
                            device_value,
                            key=device_value.key.removesuffix("_raw"),
                            raw_value=None,
                        )
                    continue

                result[sensor_definition.key] = replace(
                    self._last_stored_energies.data.get(sensor_definition.key)
                )
                continue

            if (last_power := self._last_snapshot.data.get("power")) is None or (
                current_power := result.get("power")
            ) is None:
                return result

            # Zeitdifferenz in Stunden berechnen
            timediff_hours = (
                now - self._last_snapshot.timestamp
            ).total_seconds() / 3_600

            # Trapezregel
            if current_power.phys_value is not None and timediff_hours > 0:
                additional_energy = (
                    (last_power.phys_value + current_power.phys_value)
                    / 2
                    * timediff_hours
                    / 1_000
                )
                new_energy = replace(
                    self._last_snapshot.data.get(sensor_definition.key)
                )
                new_energy.phys_value += additional_energy
                result[sensor_definition.key] = new_energy

        return result

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            raw_data = await self._async_get_raw_pump_data(HTTP_REQS)
            if raw_data is None:
                raise UpdateFailed("Unable to retrieve data from Remko")

            sanitize_data = self._sanitize_data(raw_data)
            now = dt.now()
            result = await self.async_energy_calculation(sanitize_data, now)

            self._last_snapshot = CoordinatorSnapshot(
                data=deepcopy(result), timestamp=now
            )

            _LOGGER.debug("%s", _format_decoded_data(result))

            self._storage_dirty = True
            # Timer erst nach dem ersten erfolgreichen Update starten.
            if self._unsub_storage is None:
                self._unsub_storage = async_track_time_interval(
                    self.hass,
                    self._async_storage_flush,
                    timedelta(minutes=10),
                    cancel_on_shutdown=True,
                )
            return deepcopy(result)
        except UpdateFailed:
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err, exc_info=True)
            raise UpdateFailed("Unexpected error communicating with Remko") from err

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
            response = await self._async_set_raw_pump_data(
                sensor_definition.http_req, values
            )
        except Exception:
            _LOGGER.error(
                f"Request for {sensor_definition.key} of ID {sensor_definition.http_req} with {values}"
            )
            return None

        return response.get(str(sensor_definition.http_req))


def _format_decoded_data(data: dict[str, DeviceValue]) -> str:
    lines = ["Decoded data:"]

    for key, value in sorted(data.items()):
        lines.append(
            f"  {key:<25} = {_format_log_value(value.phys_value):<12} (raw: {value.raw_value})"
        )

    return "\n".join(lines)


def _format_log_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def parse_datetime(raw: Any) -> datetime | None:
    """Parse an ISO format datetime string into a datetime object."""
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw)
    except TypeError, ValueError:
        return None
