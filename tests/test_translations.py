"""Tests for translation key consistency."""

import json
from pathlib import Path
from typing import Any

import pytest

from custom_components.remko_http.const import (
    BUTTONS,
    ENERGY_SENSORS,
    ENERGY_SENSORS_DEVICE_RAW,
    NUMBERS,
    SELECTORS,
    SENSORS,
)

INTEGRATION_DIR = Path(__file__).parents[1] / "custom_components" / "remko_http"


def _load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object from a translation file."""
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def _leaf_keys(value: Any, prefix: tuple[str, ...] = ()) -> set[tuple[str, ...]]:
    """Return the paths to all translated leaf values."""
    if not isinstance(value, dict):
        return {prefix}

    return {
        leaf
        for key, child in value.items()
        for leaf in _leaf_keys(child, (*prefix, key))
    }


@pytest.mark.parametrize("language", ["de", "en"])
def test_translation_keys_match_strings(language: str) -> None:
    """Every language must have exactly the keys declared in strings.json."""
    source = _load_json(INTEGRATION_DIR / "strings.json")
    translation = _load_json(INTEGRATION_DIR / "translations" / f"{language}.json")

    assert _leaf_keys(translation) == _leaf_keys(source)


def test_entity_translation_keys_match_definitions() -> None:
    """Entity translation keys must match the configured entity definitions."""
    entity_translations = _load_json(INTEGRATION_DIR / "strings.json")["entity"]
    expected_keys = {
        "button": {definition.key for definition in BUTTONS},
        "number": {definition.key for definition in NUMBERS},
        "select": {definition.key for definition in SELECTORS},
        "sensor": {
            definition.key
            for definition in (
                *SENSORS,
                *ENERGY_SENSORS,
                *ENERGY_SENSORS_DEVICE_RAW,
            )
        },
    }

    assert {
        platform: set(translations)
        for platform, translations in entity_translations.items()
    } == expected_keys
