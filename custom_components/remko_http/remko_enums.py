"""Constants for Remko Heatpump integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, StrEnum

from homeassistant.components.sensor import (
    SensorDeviceClass,
)


@dataclass
class DeviceValue:
    key: str
    phys_value: int | float | str | None = None
    raw_value: str | None = None


@dataclass
class CoordinatorSnapshot:
    data: dict[str, DeviceValue]
    timestamp: datetime | None


class RemkoDataType(Enum):
    UINT8 = (1, False)
    INT8 = (1, True)
    UINT16 = (2, False)
    INT16 = (2, True)
    UINT32 = (4, False)
    INT32 = (4, True)

    @property
    def response_size(self) -> int:
        return self.value[0]

    @property
    def signed(self) -> bool:
        return self.value[1]


class ScaleType(StrEnum):
    TEMPERATURE = SensorDeviceClass.TEMPERATURE
    POWER = SensorDeviceClass.POWER
    DEFAULT = "default"

    @property
    def scale(self) -> int | float:
        return {
            "default": 1,
            SensorDeviceClass.TEMPERATURE: 0.1,
            SensorDeviceClass.POWER: 100,
        }[self]


class RoomClimateMode(StrEnum):
    AUTO = "auto"
    HEATING = "heating"
    STANDBY = "standby"
    COOLING = "cooling"

    @property
    def hex_value(self) -> str | None:
        try:
            return {
                RoomClimateMode.AUTO: "01",
                RoomClimateMode.HEATING: "02",
                RoomClimateMode.STANDBY: "03",
                RoomClimateMode.COOLING: "04",
            }[self]
        except KeyError:
            return None

    @classmethod
    def from_hex(cls, value: str) -> RoomClimateMode | str:
        for state in cls:
            if state.hex_value == value:
                return state

        return f"Status N/A: {value}"


class HotWaterReqState(StrEnum):
    STANDBY = "standby"
    ACTIVE = "active"

    @property
    def hex_value(self) -> str | None:
        try:
            return {
                HotWaterReqState.STANDBY: "00",
                HotWaterReqState.ACTIVE: "01",
            }[self]
        except KeyError:
            return None

    @classmethod
    def from_hex(cls, value: str) -> HotWaterReqState | str:
        for state in cls:
            if state.hex_value == value:
                return state

        return f"Status N/A: {value}"


class SwitchState(StrEnum):
    OFF = "off"
    ON = "on"

    @property
    def hex_value(self) -> str | None:
        try:
            return {
                SwitchState.OFF: "00",
                SwitchState.ON: "01",
            }[self]
        except KeyError:
            return None

    @classmethod
    def from_hex(cls, value: str) -> SwitchState | str:
        for state in cls:
            if state.hex_value == value:
                return state

        return f"Status N/A: {value}"


class OperatingState(StrEnum):
    UNKNOWN = "unknown"
    FAULT = "fault"
    DEFROST = "defrosting"
    DEFROSTBUFFER = "defrost_buffer"
    DHWBUFFER = "dhw_buffer"
    ENERGYSTORAGE = "energy_storage"
    HEATING = "heating"
    COOLING = "cooling"
    CIRCULATION = "circulation"
    STANDBY = "standby"
    FROSTPROTECT = "frost_protection"
    READY = "ready"

    @property
    def hex_value(self) -> str | None:
        try:
            return {
                OperatingState.UNKNOWN: "00",
                OperatingState.FAULT: "01",
                OperatingState.DEFROST: "02",
                OperatingState.DEFROSTBUFFER: "03",
                OperatingState.DHWBUFFER: "04",
                OperatingState.ENERGYSTORAGE: "05",
                OperatingState.HEATING: "06",
                OperatingState.COOLING: "07",
                OperatingState.CIRCULATION: "09",
                OperatingState.STANDBY: "0A",
                OperatingState.FROSTPROTECT: "0C",
                OperatingState.READY: "40",
            }[self]
        except KeyError:
            return None

    @classmethod
    def from_hex(cls, value: str) -> OperatingState | str:
        for state in cls:
            if state.hex_value == value:
                return state

        return f"Status N/A: {value}"
