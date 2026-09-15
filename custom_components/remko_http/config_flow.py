"""Config flow for Remko HTTP integration."""

from __future__ import annotations

from ipaddress import ip_address
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


def _validate_host(host: str):
    try:
        ip_address(host)
    except Exception as err:
        raise ConnectionError(f"Wrong IP-Adress: {err}") from err


class RemkoHeatPumpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Remko-Heatpump."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            host = user_input["host"]
            try:
                _validate_host(host)
            except ConnectionError as err:
                errors["base"] = str(err)

            if not errors:
                return self.async_create_entry(
                    title=f"Remko ({host})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("host"): str,
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): vol.All(int, vol.Range(min=10, max=60)),
                }
            ),
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
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            current_host = self._config_entry.data.get(CONF_HOST)

            if host != current_host:
                try:
                    _validate_host(host)
                except ConnectionError as err:
                    errors["base"] = str(err)

            if not errors:
                # Store settings in entry data and keep options a valid mapping.
                self.hass.config_entries.async_update_entry(
                    self._config_entry,
                    data={
                        **self._config_entry.data,
                        **user_input,
                    },
                )
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST, default=self._config_entry.data.get(CONF_HOST, "")
                    ): str,
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self._config_entry.data.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(int, vol.Range(min=10, max=60)),
                }
            ),
            errors=errors,
        )
