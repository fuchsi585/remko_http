"""Tests for the Remko utils."""

import pytest

from custom_components.remko_http.remko_enums import (
    RemkoDataType,
    ScaleType
)

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
        (1.7, ScaleType.TEMPERATURE, "000F"), # auf 1.5
        (200, ScaleType.POWER, "0002"),
    ],
)
def test_decode_device_value_scaling(value, scale, expected) -> None:
    """Test sensor values are decoded and scaled."""
    from custom_components.remko_http.utils import encode, round_number

    assert encode(int(round_number(value) / scale.scale), RemkoDataType.UINT16) == expected