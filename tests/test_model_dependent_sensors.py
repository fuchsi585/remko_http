"""Regression tests for model-specific sensor request IDs."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.remko_http.const import SENSORS, get_http_reqs
from custom_components.remko_http.coordinator import RemkoCoordinator
from custom_components.remko_http.remko_enums import ModelType
from custom_components.remko_http.sensor import RemkoSensor


@pytest.mark.parametrize(
    ("model", "expected_id", "expected_raw", "expected_temperature"),
    [
        (ModelType.WKF_70_F, 5581, "00E2", 22.6),
        (ModelType.WKF_120_F, 5476, "00FB", 25.1),
        (ModelType.WKF_120_DUO, 5476, "00FB", 25.1),
        (ModelType.NO_NAME, 5476, "00FB", 25.1),
        ("Status N/A: AB", 5476, "00FB", 25.1),
        (None, 5476, "00FB", 25.1),
    ],
    ids=["wkf70", "wkf120", "duo", "unknown-model", "unknown-code", "missing-model"],
)
@pytest.mark.asyncio
async def test_model_specific_return_temperature(
    model: ModelType | str | None,
    expected_id: int,
    expected_raw: str,
    expected_temperature: float,
) -> None:
    """Polling, decoding and entity attributes must agree on the selected ID."""
    entry = SimpleNamespace(entry_id="remko", data={"host": "127.0.0.1"})
    coordinator = RemkoCoordinator(MagicMock(), entry)
    if model is not None:
        coordinator._device_info["model"] = model
    coordinator._unsub_storage = MagicMock()
    # Distinct values catch decoding the default ID despite requesting the override.
    coordinator._async_real_all_raw_pump_data = AsyncMock(
        return_value={5476: "00FB", 5581: "00E2", 5039: "00FA"}
    )

    values = await coordinator._async_update_data()

    queries = coordinator._async_real_all_raw_pump_data.await_args.args[0]
    expected_queries = (set(get_http_reqs()) - {5476}) | {expected_id}
    assert set(queries) == expected_queries
    assert len(queries) == len(set(queries))
    assert values["mixed_return_temp"].raw_value == expected_raw
    assert values["mixed_return_temp"].phys_value == pytest.approx(expected_temperature)
    # An unrelated sensor keeps its usual decoding.
    assert values["water_temp"].phys_value == 25.0

    definition = next(sensor for sensor in SENSORS if sensor.key == "mixed_return_temp")
    coordinator.data = values
    entity = RemkoSensor(coordinator, definition, entry)
    assert entity.native_value == pytest.approx(expected_temperature)
    assert entity.extra_state_attributes == {
        "http_req": expected_id,
        "raw_value": expected_raw,
    }
    # Resolving one model must not mutate the shared definition's default.
    assert definition.http_req == 5476
