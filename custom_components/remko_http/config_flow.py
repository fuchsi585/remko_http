"""Config flow for Remko Heatpump integration."""

from __future__ import annotations

import logging
import ipaddress
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_HOST, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=10, max=60)
        ),
    }
)


async def _validate_connection(host: str) -> None:
    try:
        ipaddress.ip_address(host)
    except ValueError as err:
        raise ConnectionError(f"Wrong IP-Adress: {err}") from err

    # try:
    #     response = httpx.get(f"http://{host}/cgi-bin/webapi.cgi", timeout=0.3)
    # except httpx.TimeoutException as err:
    #     raise ConnectionError(f"Timeut: {host} not reachable!") from err

    # if response.status_code != 200:
    #     raise ConnectionError(
    #         f"Negative Response: {host} with status-code {response.status_code}"
    #     )


class RemkoHeatPumpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Remko-Heatpump."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input["host"]

            try:
                await _validate_connection(host)
            except ConnectionError as err:
                errors["base"] = str(err)

            if not errors:
                await self.async_set_unique_id(f"{host}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Remko ({host})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return RemkoHeatPumpOptionsFlow(config_entry)


class RemkoHeatPumpOptionsFlow(config_entries.OptionsFlow):
    """Handle options (reconfiguration after setup)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            host = user_input[CONF_HOST]

            # current_host = self._config_entry.data.get("host")

            # Update entry data for host, store rest in options
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data={**self._config_entry.data, CONF_HOST: host},
            )
            return self.async_create_entry(
                title="",
                data={
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                },
            )

        def _current(key, default):
            return self._config_entry.options.get(
                key, self._config_entry.data.get(key, default)
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST, default=self._config_entry.data.get(CONF_HOST, "")
                ): str,
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=_current(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.All(int, vol.Range(min=10, max=60)),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors={})
