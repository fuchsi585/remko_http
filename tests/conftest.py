"""Pytest configuration for tests without a Home Assistant installation."""

from __future__ import annotations

import sys
import types


# ---------------------------------------------------------------------------
# Home Assistant stubs
# ---------------------------------------------------------------------------

homeassistant = types.ModuleType("homeassistant")
homeassistant.__path__ = []

homeassistant_const = types.ModuleType("homeassistant.const")


class Platform:
    """Minimal Home Assistant Platform stub."""

    NUMBER = "number"
    SELECT = "select"
    SENSOR = "sensor"


homeassistant_const.Platform = Platform


homeassistant_core = types.ModuleType("homeassistant.core")


class HomeAssistant:
    """Minimal Home Assistant stub."""


homeassistant_core.HomeAssistant = HomeAssistant


homeassistant_config_entries = types.ModuleType("homeassistant.config_entries")


class ConfigEntry:
    """Minimal ConfigEntry stub."""

    data: dict = {}
    options: dict = {}


homeassistant_config_entries.ConfigEntry = ConfigEntry


# ---------------------------------------------------------------------------
# Home Assistant update coordinator stub
# ---------------------------------------------------------------------------

homeassistant_helpers = types.ModuleType("homeassistant.helpers")
homeassistant_helpers.__path__ = []

homeassistant_update_coordinator = types.ModuleType(
    "homeassistant.helpers.update_coordinator"
)


class DataUpdateCoordinator:
    """Minimal DataUpdateCoordinator stub."""

    def __init__(
        self,
        hass=None,
        logger=None,
        name=None,
        update_interval=None,
        **kwargs,
    ) -> None:
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval

    async def async_shutdown(self) -> None:
        """Shut down the coordinator."""


class UpdateFailed(Exception):
    """Minimal UpdateFailed stub."""


homeassistant_update_coordinator.DataUpdateCoordinator = DataUpdateCoordinator
homeassistant_update_coordinator.UpdateFailed = UpdateFailed


# ---------------------------------------------------------------------------
# Home Assistant httpx client stub
# ---------------------------------------------------------------------------

homeassistant_httpx_client = types.ModuleType(
    "homeassistant.helpers.httpx_client"
)


def get_async_client(*args, **kwargs):
    """Return a minimal HTTP client stub."""
    return None


homeassistant_httpx_client.get_async_client = get_async_client


# ---------------------------------------------------------------------------
# httpx stub
# ---------------------------------------------------------------------------

httpx = types.ModuleType("httpx")


class HTTPStatusError(Exception):
    """Minimal httpx HTTPStatusError stub."""


class RequestError(Exception):
    """Minimal httpx RequestError stub."""


class InvalidURL(Exception):
    """Minimal httpx InvalidURL stub."""


httpx.HTTPStatusError = HTTPStatusError
httpx.RequestError = RequestError
httpx.InvalidURL = InvalidURL


# ---------------------------------------------------------------------------
# Register stubs before importing the integration.
# ---------------------------------------------------------------------------

sys.modules["homeassistant"] = homeassistant
sys.modules["homeassistant.const"] = homeassistant_const
sys.modules["homeassistant.core"] = homeassistant_core
sys.modules["homeassistant.config_entries"] = homeassistant_config_entries
sys.modules["homeassistant.helpers"] = homeassistant_helpers
sys.modules["homeassistant.helpers.update_coordinator"] = (
    homeassistant_update_coordinator
)
sys.modules["homeassistant.helpers.httpx_client"] = homeassistant_httpx_client
sys.modules["httpx"] = httpx