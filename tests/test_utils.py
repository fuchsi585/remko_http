"""Tests for the Remko utils."""

import pytest

from custom_components.remko_http.remko_enums import RemkoDataType, ScaleType


@pytest.mark.parametrize(
    ("hex_value", "data_type", "expected"),
    [
        ("0000", RemkoDataType.UINT16, 0),
        ("0001", RemkoDataType.UINT16, 1),
        ("FFFF", RemkoDataType.INT16, -1),
        ("8000", RemkoDataType.INT16, -32768),
        ("00000064", RemkoDataType.UINT32, 100),
    ],
)
def test_decode_numeric_value(hex_value, data_type, expected) -> None:
    """Test the numeric protocol decoding used by the coordinator."""
    from custom_components.remko_http.utils import decode

    assert decode(hex_value, data_type) == expected


@pytest.mark.parametrize(
    ("hex_value", "scale", "expected"),
    [
        ("000A", ScaleType.TEMPERATURE, 1.0),
        ("0002", ScaleType.POWER, 200),
    ],
)
def test_decode_device_value_scaling(hex_value, scale, expected) -> None:
    """Test sensor values are decoded and scaled."""
    from custom_components.remko_http.utils import decode

    assert decode(hex_value, RemkoDataType.UINT16) * scale.scale == expected


@pytest.mark.parametrize(
    ("value", "data_type", "expected"),
    [
        (0, RemkoDataType.UINT16, "0000"),
        (1, RemkoDataType.UINT16, "0001"),
        (-1, RemkoDataType.INT16, "FFFF"),
        (-32768, RemkoDataType.INT16, "8000"),
        (100, RemkoDataType.UINT32, "00000064"),
    ],
)
def test_encode_numeric_value(value, data_type, expected) -> None:
    """Test the numeric protocol decoding used by the coordinator."""
    from custom_components.remko_http.utils import encode

    assert encode(value, data_type) == expected


@pytest.mark.parametrize(
    ("value", "scale", "expected"),
    [
        (1.0, ScaleType.TEMPERATURE, "000A"),
        (1.2, ScaleType.TEMPERATURE, "000A"),
        (1.7, ScaleType.TEMPERATURE, "000F"),  # auf 1.5
        (200, ScaleType.POWER, "0002"),
    ],
)
def test_encode_device_value_scaling(value, scale, expected) -> None:
    """Test sensor values are decoded and scaled."""
    from custom_components.remko_http.utils import encode, round_number

    assert (
        encode(int(round_number(value) / scale.scale), RemkoDataType.UINT16) == expected
    )


@pytest.mark.parametrize("value", ["not-hex", "0"])
def test_decode_rejects_invalid_hex(value: str) -> None:
    """Malformed hexadecimal device values must not be decoded silently."""
    from custom_components.remko_http.utils import decode

    with pytest.raises(ValueError):
        decode(value, RemkoDataType.UINT16)


@pytest.mark.parametrize(
    ("value", "data_type"),
    [("00", RemkoDataType.UINT16), ("000000", RemkoDataType.UINT16)],
)
def test_decode_rejects_wrong_response_size(
    value: str, data_type: RemkoDataType
) -> None:
    """A valid hex string still needs the exact protocol-defined byte length."""
    from custom_components.remko_http.utils import decode

    with pytest.raises(ValueError, match="expects 2 bytes"):
        decode(value, data_type)


@pytest.mark.parametrize(
    ("value", "data_type"),
    [
        (-1, RemkoDataType.UINT8),
        (256, RemkoDataType.UINT8),
        (-32769, RemkoDataType.INT16),
        (32768, RemkoDataType.INT16),
    ],
)
def test_encode_rejects_values_outside_data_type(
    value: int, data_type: RemkoDataType
) -> None:
    """Values outside a protocol type's range produce a clear ValueError."""
    from custom_components.remko_http.utils import encode

    with pytest.raises(ValueError, match="does not fit"):
        encode(value, data_type)


@pytest.mark.parametrize("value", [None, "", "invalid", 123])
def test_parse_datetime_returns_none_for_invalid_values(value) -> None:
    """Missing or malformed storage timestamps are handled safely."""
    from custom_components.remko_http.utils import parse_datetime

    assert parse_datetime(value) is None
