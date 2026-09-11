"""Consistency tests for Remko Heatpump constants."""

from collections import defaultdict

from custom_components.remko_http.const import (
    BUTTONS,
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ENERGY_SENSORS,
    ENERGY_SENSORS_DEVICE_RAW,
    HTTP_REQ_SERIAL_NUMBER,
    HTTP_REQS,
    NUMBERS,
    SELECTORS,
    SENSORS,
    SLEEP_TIME_AFTER_SET_REQ,
    STORAGE_KEYS,
)
from custom_components.remko_http.remko_enums import RemkoDataType, ScaleType
from custom_components.remko_http.utils import decode, encode

ALL_DEFINITIONS = (
    *BUTTONS,
    *SELECTORS,
    *SENSORS,
    *NUMBERS,
    *ENERGY_SENSORS,
    *ENERGY_SENSORS_DEVICE_RAW,
)
READ_DEFINITIONS = (*BUTTONS, *SENSORS, *ENERGY_SENSORS_DEVICE_RAW)


def test_constants() -> None:
    """Test integration constants."""
    assert CONF_HOST == "host"
    assert CONF_SCAN_INTERVAL == "scan_interval"
    assert DOMAIN == "remko_http"
    assert DEFAULT_SCAN_INTERVAL == 20
    assert SLEEP_TIME_AFTER_SET_REQ == 0.4
    assert HTTP_REQ_SERIAL_NUMBER == 5700


def test_all_protocol_data_types() -> None:
    """Test the size and signedness of every supported protocol type."""
    assert {
        data_type: (data_type.response_size, data_type.signed)
        for data_type in RemkoDataType
    } == {
        RemkoDataType.UINT8: (1, False),
        RemkoDataType.INT8: (1, True),
        RemkoDataType.UINT16: (2, False),
        RemkoDataType.INT16: (2, True),
        RemkoDataType.UINT32: (4, False),
        RemkoDataType.INT32: (4, True),
    }


def test_all_protocol_data_types_round_trip() -> None:
    """Test that the numeric decoder handles every supported protocol type."""
    for data_type in RemkoDataType:
        bits = data_type.response_size * 8
        minimum = -(2 ** (bits - 1)) if data_type.signed else 0
        maximum = 2 ** (bits - int(data_type.signed)) - 1
        for value in (minimum, 0, maximum):
            assert decode(encode(value, data_type), data_type) == value


def test_all_scaling_factors() -> None:
    """Test every supported physical-value scaling factor."""
    assert {scale_type: scale_type.scale for scale_type in ScaleType} == {
        ScaleType.DEFAULT: 1,
        ScaleType.TEMPERATURE: 0.1,
        ScaleType.POWER: 100,
    }


def test_entity_keys_are_unique() -> None:
    """Entity keys must be globally unique across all platforms."""
    keys = [definition.key for definition in ALL_DEFINITIONS]
    assert len(keys) == len(set(keys))


def test_http_request_ids_are_valid_and_complete() -> None:
    """Every entity has a valid request ID and is included in the poll list."""
    definition_ids = {definition.http_req for definition in ALL_DEFINITIONS}

    assert None not in definition_ids
    assert all(
        type(http_req) is int and 0 < http_req <= 0xFFFF for http_req in HTTP_REQS
    )
    assert set(HTTP_REQS) == definition_ids


def test_shared_http_ids_have_consistent_decoders() -> None:
    """Definitions sharing an ID must agree on its wire representation."""
    definitions_by_id = defaultdict(list)
    for definition in ALL_DEFINITIONS:
        definitions_by_id[definition.http_req].append(definition)

    for definitions in definitions_by_id.values():
        options = {definition.option for definition in definitions if definition.option}
        response_sizes = {
            definition.data_type.response_size
            for definition in definitions
            if hasattr(definition, "data_type") and definition.data_type
        }
        scales = {definition.scale_type for definition in definitions}
        assert len(options) <= 1
        assert len(response_sizes) <= 1
        assert len(scales) <= 1


def test_read_and_enable_keys_reference_decoded_entities() -> None:
    """Write and enable references must point to values decoded by the coordinator."""
    readable_by_key = {definition.key: definition for definition in READ_DEFINITIONS}

    for definition in (*BUTTONS, *SELECTORS, *NUMBERS):
        assert definition.read_key in readable_by_key
        assert definition.http_req == readable_by_key[definition.read_key].http_req

    for definition in BUTTONS:
        if definition.enable_key is None:
            assert definition.enable_value is None
            continue
        enabled_by = readable_by_key[definition.enable_key]
        assert enabled_by.option is not None
        assert isinstance(definition.enable_value, enabled_by.option)


def test_number_ranges_are_valid_and_encodable() -> None:
    """Number bounds and increments must be usable with their wire format."""
    for definition in NUMBERS:
        assert definition.min_value < definition.max_value
        assert definition.step > 0
        assert (definition.max_value - definition.min_value) % definition.step == 0
        for value in (definition.min_value, definition.max_value):
            raw_value = int(value / definition.scale_type.scale)
            assert (
                decode(encode(raw_value, definition.data_type), definition.data_type)
                == raw_value
            )


def test_read_definitions_have_a_decoder() -> None:
    """Every polled entity must define either enum or numeric decoding."""
    for definition in READ_DEFINITIONS:
        if definition.option is not None:
            assert callable(getattr(definition.option, "from_hex", None))
            assert definition.data_type is not None
        else:
            assert definition.data_type is not None
            assert definition.scale_type is not None


def test_enum_decoders_round_trip() -> None:
    """Every configured enum value must round-trip through its protocol hex value."""
    enum_types = {
        definition.option for definition in ALL_DEFINITIONS if definition.option
    }

    for enum_type in enum_types:
        for member in enum_type:
            assert member.hex_value is not None
            assert enum_type.from_hex(member.hex_value) is member


def test_energy_sensor_dependencies_are_consistent() -> None:
    """Calculated energy sensors must reference valid power and raw sensors."""
    sensors_by_key = {definition.key: definition for definition in SENSORS}
    raw_by_key = {
        definition.key: definition for definition in ENERGY_SENSORS_DEVICE_RAW
    }

    for definition in ENERGY_SENSORS:
        assert definition.intergrated_power in sensors_by_key
        assert definition.source_key in raw_by_key
        assert definition.http_req == raw_by_key[definition.source_key].http_req
        assert definition.max_energy_stored_diff is not None
        assert definition.max_energy_stored_diff > 0


def test_storage_keys_reference_calculated_energy_sensors() -> None:
    """Only calculated energy values may be persisted."""
    energy_keys = {definition.key for definition in ENERGY_SENSORS}

    assert STORAGE_KEYS
    assert len(STORAGE_KEYS) == len(set(STORAGE_KEYS))
    assert set(STORAGE_KEYS) <= energy_keys
