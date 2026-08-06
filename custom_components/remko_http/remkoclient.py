from __future__ import annotations


import logging
from typing import Any
from httpx import HTTPStatusError, RequestError, InvalidURL

from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client

_LOGGER = logging.getLogger(__name__)


class RemkoHttpClient:
    def __init__(self, host: str) -> None:
        self._session = None
        self._last_error = None
        self._last_query = None
        self._last_response = None
        self._payload = {"SMT_ID": "0000000000000000"}
        self._timeout = 10.0
        self._url = f"http://{host}/cgi-bin/webapi.cgi"

    async def async_setup_client(self, hass: HomeAssistant = None) -> None:
        self._session = get_async_client(hass, verify_ssl=False)

    async def async_get_firmware(self) -> str:
        response = await self.async_get_pump_data(["SMT_VERSION"])
        return response.get("SMT_VERSION", "unknown")

    async def async_get_serial_number(self) -> str:
        response = await self.async_get_pump_data([5700])
        return response.get(5700, "unknown")

    async def async_get_pump_data(self, queries: list[int] = None) -> dict | None:
        if not queries or not self._session:
            _LOGGER.warning("HttpClient not initialized or queries is empty!")
            return None

        result = {}
        payload = self._payload
        payload.update({"query_list": queries})
        self._last_query = queries

        try:
            resp = await self._session.post(
                self._url, json=payload, timeout=self._timeout
            )
            resp.raise_for_status()
            data = resp.json()
            if "values" in data:
                data.update(data.pop("values"))
                for query_id in queries:
                    result[query_id] = data.get(str(query_id), None)

                self._last_response = data
                _LOGGER.debug(f"Last response: {self._last_response}")
        except (HTTPStatusError, InvalidURL, RequestError) as err:
            _LOGGER.error(f"Remko-Client error: {repr(err)}")
            self._last_error = err
            self._last_response = None
            return {}

        return dict(result)

    async def async_set_pump_data(self, remko_id: int, values: dict) -> dict | Any:
        payload = self._payload
        payload.update({"query_list": remko_id})
        payload.update({"values": values})
        self._last_query = remko_id

        try:
            resp = await self._session.post(
                self._url, json=payload, timeout=self._timeout
            )
            resp.raise_for_status()
            self._last_response = resp.json()

            _LOGGER.debug(f"Last response: {self._last_response}")
        except (HTTPStatusError, InvalidURL, RequestError) as err:
            _LOGGER.error(f"Remko-Client error: {repr(err)}")
            self._last_error = err
            self._last_response = None
            return {}

        return self._last_response
