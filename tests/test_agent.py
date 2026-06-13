from unittest.mock import patch, MagicMock
import pytest
from agent import Agent

_MCP_URI = "http://localhost:8000"

_TOOLS_LIST_RESPONSE = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "tools": [
            {
                "name": "get_climate_data",
                "description": "Retrieve climate data for a location.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "number"},
                        "lon": {"type": "number"},
                    },
                    "required": ["lat", "lon"],
                },
            }
        ]
    },
}


def test_setup_tool_registry_from_mcp():
    mock_response = MagicMock()
    mock_response.json.return_value = _TOOLS_LIST_RESPONSE

    with patch("httpx.post", return_value=mock_response) as mock_post:
        agent = Agent("test", mcp_uri=_MCP_URI)
        mock_post.assert_called_once_with(
            _MCP_URI, json={"jsonrpc": "2.0", "method": "tools/list", "params": {}}
        )

    assert "get_climate_data" in agent.tool_registry
    fn, desc = agent.tool_registry["get_climate_data"]
    assert callable(fn)
    assert desc == "Retrieve climate data for a location."


def test_setup_tool_registry_from_registry():
    registry = {"mock_tool": (lambda: None, "A mock tool")}
    agent = Agent("test", tool_registry=registry)
    assert agent.tool_registry is registry


def test_setup_tool_registry_raises_without_args():
    with pytest.raises(Exception):
        Agent("test")
