"""Tests for the Remko coordinator."""

import pytest

from custom_components.remko_http.const import Factor
from custom_components.remko_http.coordinator import RemkoCoordinator


@pytest.mark.parametrize(
    ("hex_value", "factor", "expected"),
    [
        ("0000", Factor.TEMP, 0.0),
        ("0001", Factor.TEMP, 0.1),
        ("000A", Factor.TEMP, 1.0),
        ("0064", Factor.TEMP, 10.0),
        ("03E8", Factor.TEMP, 100.0),
    ],
)
def test_hex2number_positive(
    hex_value: str,
    factor: Factor,
    expected: float,
) -> None:
    """Test conversion of positive hexadecimal values."""
    assert RemkoCoordinator._hex2number(hex_value, factor) == expected


@pytest.mark.parametrize(
    ("hex_value", "factor", "expected"),
    [
        ("FFFF", Factor.TEMP, -0.1),
        ("FFFE", Factor.TEMP, -0.2),
        ("FFF6", Factor.TEMP, -1.0),
        ("FF9C", Factor.TEMP, -10.0),
    ],
)
def test_hex2number_negative(
    hex_value: str,
    factor: Factor,
    expected: float,
) -> None:
    """Test conversion of negative hexadecimal values."""
    assert RemkoCoordinator._hex2number(hex_value, factor) == expected


def test_hex2number_signed_boundary() -> None:
    """Test signed 16-bit boundaries."""
    assert round(RemkoCoordinator._hex2number("7FFF", Factor.TEMP), 1) == 3276.7
    assert RemkoCoordinator._hex2number("8000", Factor.TEMP) == -3276.8


@pytest.mark.parametrize(
    "hex_value",
    [
        "not-hex",
        "",
        "XYZ",
    ],
)
def test_hex2number_invalid_value(hex_value: str) -> None:
    """Test invalid hexadecimal input."""
    with pytest.raises(ValueError):
        RemkoCoordinator._hex2number(hex_value, Factor.TEMP)


@pytest.mark.parametrize(
    ("hex_value", "factor", "expected"),
    [
        ("0001", Factor.POWER, 100),
        ("000A", Factor.POWER, 1000),
    ],
)
def test_hex2number_power(
    hex_value: str,
    factor: Factor,
    expected: float,
) -> None:
    """Test conversion using the power factor."""
    assert RemkoCoordinator._hex2number(hex_value, factor) == expected
