"""Number platform for Remko."""

from __future__ import annotations

import logging
import asyncio

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SWITCHES,
    SLEEP_TIME_AFTER_SET_REQ,
    RemkoSwitchDef,
)
from .coordinator import RemkoCoordinator, DeviceValue


_LOGGER = logging.getLogger(__name__)
