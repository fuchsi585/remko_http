from __future__ import annotations

from datetime import datetime
from typing import Any

from .remko_enums import DeviceValue, RemkoDataType


def decode(value: str, data_type: RemkoDataType) -> int:
    raw = bytes.fromhex(value)

    if len(raw) != data_type.response_size:
        raise ValueError(
            f"{data_type.name} expects {data_type.response_size} bytes, got {len(raw)}"
        )

    return int.from_bytes(
        raw,
        byteorder="big",
        signed=data_type.signed,
    )


def encode(value: int, data_type: RemkoDataType) -> str:
    try:
        raw = value.to_bytes(
            length=data_type.response_size,
            byteorder="big",
            signed=data_type.signed,
        )
    except OverflowError as err:
        raise ValueError(f"{value} does not fit into {data_type.name}") from err

    return raw.hex().upper()


def format_decoded_data(data: dict[str, DeviceValue]) -> str:
    lines = ["Decoded data:"]

    for key, value in sorted(data.items()):
        physical_value = format_log_value(value.phys_value)
        lines.append(f"  {key:<25} = {physical_value:<12} (raw: {value.raw_value})")

    return "\n".join(lines)


def format_log_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def parse_datetime(raw: Any) -> datetime | None:
    """Parse an ISO format datetime string into a datetime object."""
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw)
    except (TypeError, ValueError):
        return None


def round_number(value: float) -> float:
    return round(value * 2) / 2
