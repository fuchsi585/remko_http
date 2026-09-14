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


class ModelType(StrEnum):
    CODING_ERROR = "error"
    WKF_70_F = "WKF 70 (F)"
    WKF_85_A = "WKF 85 (A)"
    WKF_180_C = "WKF 180 (C)"
    WKF_120_C = "WKF 120 (C)"
    WKF_180_F = "WKF 180 (F)"
    WKF_120_F = "WKF 120 (F)"
    WKF_120_DUO = "WKF 120 Duo"
    WKF_180_DUO = "WKF 180 Duo"
    NO_NAME = "Unknown Model"

    @property
    def hex_value(self) -> str | None:
        try:
            return {
                ModelType.CODING_ERROR: "00",
                ModelType.WKF_70_F: "06",
                ModelType.WKF_85_A: "07",
                ModelType.WKF_180_C: "08",
                ModelType.WKF_120_C: "09",
                ModelType.WKF_180_F: "0A",
                ModelType.WKF_120_F: "0B",
                ModelType.WKF_120_DUO: "FD",
                ModelType.WKF_180_DUO: "FE",
                ModelType.NO_NAME: "FF",
            }[self]
        except KeyError:
            return None

    @classmethod
    def from_hex(cls, value: str) -> ModelType | str:
        for state in cls:
            if state.hex_value == value:
                return state

        return f"Status N/A: {value}"


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
    TENTH = "tenth"
    HUNDREDTH = "hundredth"
    TEN_THOUSANDTH = "ten_thousandth"
    DEFAULT = "default"

    @property
    def scale(self) -> int | float:
        return {
            "default": 1,
            "tenth": 0.1,
            "hundredth": 0.01,
            "ten_thousandth": 0.0001,
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


class HeatingCircuitStatus(StrEnum):
    AUTO = "auto"
    COMFORT = "comfort"
    STANDBY = "standby"
    ECO = "eco"
    PROTECTION = "protection"

    @property
    def hex_value(self) -> str:
        return f"{list(type(self)).index(self):02X}"

    @classmethod
    def from_hex(cls, value: str) -> HeatingCircuitStatus | str:
        try:
            return list(cls)[int(value, 16)]
        except (IndexError, ValueError):
            return f"Status N/A: {value}"


class HeatPumpStatus(StrEnum):
    READY = "ready"
    LEAD_TIME = "lead_time"
    BLOCKED = "blocked"
    LOCKOUT_TIME = "lockout_time"
    LOCKED = "locked"
    DISABLED = "disabled"

    @property
    def hex_value(self) -> str:
        return f"{list(type(self)).index(self):02X}"

    @classmethod
    def from_hex(cls, value: str) -> HeatPumpStatus | str:
        try:
            return list(cls)[int(value, 16)]
        except (IndexError, ValueError):
            return f"Status N/A: {value}"


class HeatPumpSubStatus(StrEnum):
    OFF = "off"
    COOLING = "cooling"
    HEATING = "heating"
    ALARM = "alarm"
    TRANSITION_TO_COOLING = "transition_to_cooling"
    DEFROSTING = "defrosting"
    WAITING = "waiting"
    STANDBY = "standby"
    TRANSITION_TO_HEATING = "transition_to_heating"
    STOP = "stop"
    MANUAL = "manual"
    START = "start"
    EVU_BLOCK = "evu_block"

    @property
    def hex_value(self) -> str:
        return f"{list(type(self)).index(self):02X}"

    @classmethod
    def from_hex(cls, value: str) -> HeatPumpSubStatus | str:
        try:
            return list(cls)[int(value, 16)]
        except (IndexError, ValueError):
            return f"Status N/A: {value}"


class HeatPumpMode(StrEnum):
    COOLING = "cooling"
    HEATING = "heating"

    @property
    def hex_value(self) -> str:
        return f"{list(type(self)).index(self):02X}"

    @classmethod
    def from_hex(cls, value: str) -> HeatPumpMode | str:
        try:
            return list(cls)[int(value, 16)]
        except (IndexError, ValueError):
            return f"Status N/A: {value}"


class HeatPumpLockSignal(StrEnum):
    BLOCKED = "blocked"
    RELEASED = "released"

    @property
    def hex_value(self) -> str:
        return f"{list(type(self)).index(self):02X}"

    @classmethod
    def from_hex(cls, value: str) -> HeatPumpLockSignal | str:
        try:
            return list(cls)[int(value, 16)]
        except (IndexError, ValueError):
            return f"Status N/A: {value}"


class CirculationDemandState(StrEnum):
    STANDBY = "standby"
    ACTIVE = "active"
    BLOCKED = "blocked"

    @property
    def hex_value(self) -> str:
        return f"{list(type(self)).index(self):02X}"

    @classmethod
    def from_hex(cls, value: str) -> CirculationDemandState | str:
        try:
            return list(cls)[int(value, 16)]
        except (IndexError, ValueError):
            return f"Status N/A: {value}"
