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

    BUTTON = "button"
    NUMBER = "number"
    SELECT = "select"
    SENSOR = "sensor"


class UnitOfEnergy:
    KILO_WATT_HOUR = "kWh"


class UnitOfPower:
    WATT = "W"


class UnitOfRatio:
    PERCENTAGE = "%"


class UnitOfTemperature:
    CELSIUS = "°C"
    KELVIN = "K"


class UnitOfTime:
    HOURS = "h"
    MINUTES = "min"


homeassistant_const.Platform = Platform
homeassistant_const.UnitOfEnergy = UnitOfEnergy
homeassistant_const.UnitOfPower = UnitOfPower
homeassistant_const.UnitOfRatio = UnitOfRatio
homeassistant_const.UnitOfTemperature = UnitOfTemperature
homeassistant_const.UnitOfTime = UnitOfTime

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

homeassistant_exceptions = types.ModuleType("homeassistant.exceptions")


class HomeAssistantError(Exception):
    """Minimal HomeAssistantError stub."""


class ConfigEntryNotReady(Exception):
    """Minimal ConfigEntryNotReady stub."""


homeassistant_exceptions.HomeAssistantError = HomeAssistantError
homeassistant_exceptions.ConfigEntryNotReady = ConfigEntryNotReady

# ---------------------------------------------------------------------------
# Home Assistant sensor component stub
# ---------------------------------------------------------------------------

homeassistant_components = types.ModuleType("homeassistant.components")
homeassistant_components.__path__ = []

homeassistant_sensor = types.ModuleType("homeassistant.components.sensor")


class EntityCategory:
    """Minimal Home Assistant EntityCategory stub."""

    CONFIG = "config"
    DIAGNOSTIC = "diagnostic"


class SensorDeviceClass:
    """Minimal Home Assistant SensorDeviceClass stub."""

    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    POWER = "power"
    ENERGY = "energy"
    DURATION = "duration"
    ENUM = "enum"


class SensorStateClass:
    """Minimal Home Assistant SensorStateClass stub."""

    MEASUREMENT = "measurement"
    TOTAL_INCREASING = "total_increasing"


homeassistant_sensor.EntityCategory = EntityCategory
homeassistant_sensor.SensorDeviceClass = SensorDeviceClass
homeassistant_sensor.SensorStateClass = SensorStateClass

# ---------------------------------------------------------------------------
# Home Assistant helpers stubs
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
        self.data = None

    async def async_shutdown(self) -> None:
        """Shut down the coordinator."""

    def async_set_updated_data(self, data) -> None:
        """Store updated data."""
        self.data = data


class UpdateFailed(Exception):
    """Minimal UpdateFailed stub."""


homeassistant_update_coordinator.DataUpdateCoordinator = DataUpdateCoordinator
homeassistant_update_coordinator.UpdateFailed = UpdateFailed

homeassistant_httpx_client = types.ModuleType("homeassistant.helpers.httpx_client")


def get_async_client(*args, **kwargs):
    """Return a minimal HTTP client stub."""
    return None


homeassistant_httpx_client.get_async_client = get_async_client

homeassistant_event = types.ModuleType("homeassistant.helpers.event")


def async_track_time_interval(*args, **kwargs):
    """Return a no-op unsubscribe callback."""
    return lambda: None


homeassistant_event.async_track_time_interval = async_track_time_interval

homeassistant_storage = types.ModuleType("homeassistant.helpers.storage")


class Store:
    """Minimal Home Assistant Store stub."""

    def __init__(self, *args, **kwargs) -> None:
        self.data = None

    async def async_load(self):
        """Load stored data."""
        return self.data

    async def async_save(self, data) -> None:
        """Save stored data."""
        self.data = data


homeassistant_storage.Store = Store

homeassistant_util = types.ModuleType("homeassistant.util")
homeassistant_dt = types.ModuleType("homeassistant.util.dt")


def now():
    """Return the current datetime."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc)


homeassistant_dt.now = now
homeassistant_util.dt = homeassistant_dt

# ---------------------------------------------------------------------------
# httpx stub
# ---------------------------------------------------------------------------

httpx = types.ModuleType("httpx")


class AsyncClient:
    """Minimal httpx AsyncClient placeholder."""


class HTTPStatusError(Exception):
    """Minimal httpx HTTPStatusError stub."""


class RequestError(Exception):
    """Minimal httpx RequestError stub."""


class InvalidURL(Exception):
    """Minimal httpx InvalidURL stub."""


httpx.AsyncClient = AsyncClient
httpx.HTTPStatusError = HTTPStatusError
httpx.RequestError = RequestError
httpx.InvalidURL = InvalidURL

# Register stubs before importing the integration.
sys.modules["homeassistant"] = homeassistant
sys.modules["homeassistant.const"] = homeassistant_const
sys.modules["homeassistant.core"] = homeassistant_core
sys.modules["homeassistant.components"] = homeassistant_components
sys.modules["homeassistant.components.sensor"] = homeassistant_sensor
sys.modules["homeassistant.config_entries"] = homeassistant_config_entries
sys.modules["homeassistant.exceptions"] = homeassistant_exceptions
sys.modules["homeassistant.helpers"] = homeassistant_helpers
sys.modules["homeassistant.helpers.update_coordinator"] = (
    homeassistant_update_coordinator
)
sys.modules["homeassistant.helpers.httpx_client"] = homeassistant_httpx_client
sys.modules["homeassistant.helpers.event"] = homeassistant_event
sys.modules["homeassistant.helpers.storage"] = homeassistant_storage
sys.modules["homeassistant.util"] = homeassistant_util
sys.modules["homeassistant.util.dt"] = homeassistant_dt
sys.modules["httpx"] = httpx
