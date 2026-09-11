"""DataUpdateCoordinator for Remk Heatpump."""

from __future__ import annotations

import asyncio
import logging
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt
from httpx import AsyncClient, HTTPStatusError, InvalidURL, RequestError

from .const import (
    BUTTONS,
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ENERGY_SENSORS,
    ENERGY_SENSORS_DEVICE_RAW,
    HTTP_REQ_SERIAL_NUMBER,
    HTTP_REQS,
    HTTP_TIMEOUT,
    MAX_DIFF_TIME_ENERGY_FACTOR,
    SENSORS,
    SLEEP_TIME_AFTER_SET_REQ,
    STORAGE_KEYS,
    STORAGE_VERSION,
    RemkoButtonDef,
    RemkoNumberDef,
    RemkoSelectDef,
    RemkoSensorDef,
)
from .remko_enums import CoordinatorSnapshot, DeviceValue
from .utils import decode, encode, format_decoded_data, parse_datetime, round_number

_LOGGER = logging.getLogger(__name__)


class RemkoCoordinator(DataUpdateCoordinator):
    """Fetches data from Remko via HTTP request."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:

        self._polling = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        self._firmware: str | None = None
        self._serial_number: str | None = None
        self._last_snapshot: CoordinatorSnapshot | None = None
        self._url: str = f"http://{entry.data.get(CONF_HOST)}/cgi-bin/webapi.cgi"
        self._session: AsyncClient | None = None
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.energy_values"
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
        _LOGGER.debug(
            f"Load last snapshot of energies at {self._last_stored_energies.timestamp}"
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
        _LOGGER.debug(
            f"Save last snapshot of energies at {snapshot.timestamp.isoformat()}"
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

        response = await self._async_read_raw_pump_data([HTTP_REQ_SERIAL_NUMBER])

        # Home Assistant erhält einen definierten Einrichtungsfehler.
        if response is None:
            raise ConfigEntryNotReady("Unable to connect to REMKO")

        self._serial_number = response.get(HTTP_REQ_SERIAL_NUMBER, "unknown")

    async def _async_read_raw_pump_data(
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

            if self._firmware is None:
                self._firmware = data.get("SMT_VERSION", "unknown")

        except (HTTPStatusError, InvalidURL, RequestError) as err:
            _LOGGER.error(f"Remko-Client error: {repr(err)}")
            return None

        return dict(result)

    async def _async_write_raw_pump_data(
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
            response = response.json()
            if "values" in response:
                response.update(response.pop("values"))
        except (HTTPStatusError, InvalidURL, RequestError) as err:
            _LOGGER.error(f"Remko-Client error: {repr(err)}")
            return None

        return response

    def _decode_device_values(self, raw_data: dict[str, str]) -> dict[str, DeviceValue]:
        data: dict = {}
        for sensor_definition in (*BUTTONS, *SENSORS, *ENERGY_SENSORS_DEVICE_RAW):
            if hex_value := raw_data.get(sensor_definition.http_req):
                entity_value = DeviceValue(sensor_definition.key)
                entity_value.raw_value = hex_value
                if sensor_definition.option:
                    entity_value.phys_value = sensor_definition.option.from_hex(
                        hex_value
                    )
                    data[entity_value.key] = entity_value
                    continue

                if sensor_definition.data_type:
                    entity_value.phys_value = (
                        decode(hex_value, sensor_definition.data_type)
                        * sensor_definition.scale_type.scale
                    )
                    data[entity_value.key] = entity_value
                    continue
                data[entity_value.key] = entity_value

        return data

    def _energy_calculation(
        self, data: dict[str, DeviceValue], now: datetime
    ) -> dict[str, DeviceValue]:
        # REMKO provides the current accumulated electrical energy via 5105.
        # Use it as the initial value and continue integrating power (5320)
        # because the device counter is not reliable for our use case.
        result: dict[str, DeviceValue] = deepcopy(data)
        max_diff_time = timedelta(seconds=self._polling * MAX_DIFF_TIME_ENERGY_FACTOR)

        for energy_definition in ENERGY_SENSORS:
            if not energy_definition.intergrated_power:
                continue

            device_energy = result.get(energy_definition.source_key)
            previous = self._last_snapshot
            last_energy = previous.data.get(energy_definition.key) if previous else None

            # Einmal initialisieren. Nachfolgende polls verwenden den Memory-Wert,
            # unabhängig davon, wann der Snapshot auf der Festplatte gespeichert wird.
            if last_energy is None or last_energy.phys_value is None:
                initial = self._last_stored_energies.data.get(energy_definition.key)

                if initial is None or initial.phys_value is None:
                    initial = device_energy
                elif device_energy is not None and device_energy.phys_value is not None:
                    stored_at = self._last_stored_energies.timestamp
                    # Wenn Differenz > 2kWh zwischen Gerät und Berechnung
                    # und Zeitstempel > polling * 4  (z.B. 80s),
                    # dann wird mit dem aktuellen Gerätewert initialisiert
                    # sonst wird der gespeicherte Wert genommen
                    if (
                        stored_at is not None
                        and stored_at.tzinfo is not None
                        and now - stored_at > max_diff_time
                        and device_energy.phys_value - initial.phys_value
                        > energy_definition.max_energy_stored_diff
                    ):
                        seconds = int((now - stored_at).total_seconds())
                        duration = (
                            f"{seconds // 3600:02d}:"
                            f"{(seconds % 3600) // 60:02d}:"
                            f"{seconds % 60:02d}"
                        )
                        _LOGGER.info(
                            "New initial value '%s': time delta (%s) and energy "
                            "difference (%s kWh > %s kWh) too large: "
                            "%s kWh → %s kWh",
                            energy_definition.key,
                            duration,
                            round(device_energy.phys_value - initial.phys_value, 2),
                            energy_definition.max_energy_stored_diff,
                            round(initial.phys_value, 2),
                            round(device_energy.phys_value, 2),
                        )
                        initial = device_energy

                if initial is not None and initial.phys_value is not None:
                    result[energy_definition.key] = replace(
                        initial, key=energy_definition.key, raw_value=None
                    )
                continue

            # Die Energie auch dann beibehalten, wenn ein Leistungswert fehlt.
            # Sobald wieder zwei aufeinanderfolgende gültige Messwerte vorliegen,
            # wird die Energieberechnung fortgesetzt.
            result[energy_definition.key] = replace(last_energy)
            last_power = previous.data.get(energy_definition.intergrated_power)
            current_power = result.get(energy_definition.intergrated_power)

            if (
                previous.timestamp is None
                or last_power is None
                or current_power is None
                or last_power.phys_value is None
                or current_power.phys_value is None
            ):
                continue

            timediff = now - previous.timestamp
            if timediff <= timedelta(0):
                continue

            if timediff > max_diff_time:
                # Hier vielleicht auf den Gerätesensor wechseln,
                # falls das gap zu groß wird?
                _LOGGER.warning(
                    "Skipping energy integration because time delta is too large: %s",
                    timediff,
                )
                continue

            # Zeitdifferenz in Stunden berechnen
            timediff_hours = timediff.total_seconds() / 3_600
            # Trapezregel
            additional_energy = (
                (last_power.phys_value + current_power.phys_value)
                / 2
                * timediff_hours
                / 1_000
            )
            result[energy_definition.key].phys_value += additional_energy

        return result

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            raw_data = await self._async_read_raw_pump_data(HTTP_REQS)
            if raw_data is None:
                raise UpdateFailed("Unable to retrieve data from Remko")

            decoded_values = self._decode_device_values(raw_data)
            now = dt.now()
            result = self._energy_calculation(decoded_values, now)

            self._last_snapshot = CoordinatorSnapshot(
                data=deepcopy(result), timestamp=now
            )

            _LOGGER.debug("%s", format_decoded_data(result))

            self._storage_dirty = True

            # Den ersten gültigen Energiewert sofort speichern.
            # Weitere Änderungen werden wie bisher alle zehn Minuten gespeichert.
            # Sofort speichern, wenn der gespeicherte Energiewert fehlt oder None ist
            # und inzwischen ein gültiger berechneter Wert vorliegt.
            if any(
                (
                    (stored := self._last_stored_energies.data.get(key)) is None
                    or stored.phys_value is None
                )
                and (value := result.get(key)) is not None
                and value.phys_value is not None
                for key in STORAGE_KEYS
            ):
                await self._async_storage_flush(now)

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

    async def async_write_to_pump(
        self,
        sensor_definition: RemkoButtonDef
        | RemkoSelectDef
        | RemkoNumberDef
        | RemkoSensorDef,
        phys_value: str,
    ) -> None:

        if sensor_definition.option:
            raw_value = sensor_definition.option(phys_value).hex_value
        else:
            raw_value = encode(
                int(round_number(phys_value) / sensor_definition.scale_type.scale),
                sensor_definition.data_type,
            )
        values = {str(sensor_definition.http_req): raw_value}

        try:
            await self._async_write_raw_pump_data(sensor_definition.http_req, values)
            await asyncio.sleep(SLEEP_TIME_AFTER_SET_REQ)

            response = await self._async_read_raw_pump_data(
                [sensor_definition.http_req]
            )
            response_data = response.get(sensor_definition.http_req)

            if sensor_definition.option:
                response_value = DeviceValue(
                    key=sensor_definition.read_key,
                    phys_value=sensor_definition.option.from_hex(response_data),
                    raw_value=response_data,
                )
            else:
                response_value = DeviceValue(
                    key=sensor_definition.read_key,
                    phys_value=decode(response_data, sensor_definition.data_type)
                    * sensor_definition.scale_type.scale,
                    raw_value=response_data,
                )

            if raw_value != response_value.raw_value:
                raise HomeAssistantError(
                    f"Request for {sensor_definition.key} of ID "
                    f"{sensor_definition.http_req} acknowledged value '{phys_value}' "
                    f"but read back '{response_value.phys_value}'"
                )
            updated_data = {
                **(self.data or {}),
                sensor_definition.read_key: response_value,
            }
            self.async_set_updated_data(updated_data)
        except Exception as err:
            _LOGGER.error(
                "Failed to write for %s of ID %s with %s: %s",
                sensor_definition.key,
                sensor_definition.http_req,
                values,
                err,
            )
            raise HomeAssistantError(f"Error writing data to heat pump: {err}") from err
