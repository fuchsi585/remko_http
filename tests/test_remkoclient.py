"""Tests for the Remko HTTP client."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.remko_http.remkoclient import RemkoHttpClient


@pytest.fixture
def client() -> RemkoHttpClient:
    """Return a Remko HTTP client."""
    return RemkoHttpClient("192.168.1.100")


@pytest.fixture
def session() -> MagicMock:
    """Return a mocked HTTP session."""
    return MagicMock()


@pytest.fixture
def response() -> MagicMock:
    """Return a mocked HTTP response."""
    response = MagicMock()
    response.raise_for_status.return_value = None
    return response


@pytest.mark.asyncio
async def test_async_setup_client(client, monkeypatch) -> None:
    """Test HTTP client setup."""
    session = MagicMock()

    monkeypatch.setattr(
        "custom_components.remko_http.remkoclient.get_async_client",
        MagicMock(return_value=session),
    )

    await client.async_setup_client("hass")

    assert client._session is session


@pytest.mark.asyncio
async def test_async_get_firmware(client) -> None:
    """Test firmware retrieval."""
    client.async_get_pump_data = AsyncMock(
        return_value={"SMT_VERSION": "4.25"}
    )

    result = await client.async_get_firmware()

    assert result == "4.25"
    client.async_get_pump_data.assert_awaited_once_with(["SMT_VERSION"])


@pytest.mark.asyncio
async def test_async_get_serial_number(client) -> None:
    """Test serial number retrieval."""
    client.async_get_pump_data = AsyncMock(
        return_value={5700: "123456789"}
    )

    result = await client.async_get_serial_number()

    assert result == "123456789"
    client.async_get_pump_data.assert_awaited_once_with([5700])


@pytest.mark.asyncio
async def test_async_get_pump_data(client, session, response) -> None:
    """Test successful pump data retrieval."""
    response.json.return_value = {
        "values": {
            "1946": "000A",
            "5039": "00FA",
        }
    }

    session.post = AsyncMock(return_value=response)
    client._session = session

    result = await client.async_get_pump_data([1946, 5039])

    assert result == {
        1946: "000A",
        5039: "00FA",
    }

    session.post.assert_awaited_once_with(
        client._url,
        json={
            "SMT_ID": "0000000000000000",
            "query_list": [1946, 5039],
        },
        timeout=10.0,
    )

    response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_async_get_pump_data_missing_value(
    client,
    session,
    response,
) -> None:
    """Test missing values in the response."""
    response.json.return_value = {
        "values": {
            "1946": "000A",
        }
    }

    session.post = AsyncMock(return_value=response)
    client._session = session

    result = await client.async_get_pump_data([1946, 5039])

    assert result == {
        1946: "000A",
        5039: None,
    }


@pytest.mark.asyncio
async def test_async_get_pump_data_without_session(client) -> None:
    """Test pump data retrieval without initialized session."""
    result = await client.async_get_pump_data([1946])

    assert result is None


@pytest.mark.asyncio
async def test_async_get_pump_data_without_queries(
    client,
    session,
) -> None:
    """Test pump data retrieval without queries."""
    client._session = session

    result = await client.async_get_pump_data([])

    assert result is None
    session.post.assert_not_called()


@pytest.mark.asyncio
async def test_async_set_pump_data(
    client,
    session,
    response,
) -> None:
    """Test successful pump data update."""
    response.json.return_value = {
        "1946": "000F",
    }

    session.post = AsyncMock(return_value=response)
    client._session = session

    result = await client.async_set_pump_data(
        1946,
        {"1946": "000F"},
    )

    assert result == {
        "1946": "000F",
    }

    session.post.assert_awaited_once_with(
        client._url,
        json={
            "SMT_ID": "0000000000000000",
            "query_list": 1946,
            "values": {"1946": "000F"},
        },
        timeout=10.0,
    )

    response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_async_set_pump_data_error(
    client,
    session,
    response,
) -> None:
    """Test error handling when setting pump data."""
    from custom_components.remko_http.remkoclient import RequestError

    response.raise_for_status.side_effect = RequestError("connection failed")

    session.post = AsyncMock(return_value=response)
    client._session = session

    result = await client.async_set_pump_data(
        1946,
        {"1946": "000F"},
    )

    assert result == {}
    assert client._last_response is None
    assert isinstance(client._last_error, RequestError)