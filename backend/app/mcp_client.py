import json
from typing import Dict, Any, List
from app.mcp_server import mcp_server

class GuardianMCPClient:
    """
    Model Context Protocol (MCP) Client for GuardianAI.
    Discovers available tools from the MCP Server, formats them for LLM function calling declarations,
    and executes tool requests via the MCP bridge.
    """
    def __init__(self):
        self.connected_server = mcp_server
        self.cached_tools: List[Dict[str, Any]] = []
        self._discover_tools()

    def _discover_tools(self):
        """
        Queries the MCP Server via list_tools() to load tool specifications.
        """
        print("[MCP Client] Discovering available tools from Guardian MCP Server...")
        self.cached_tools = self.connected_server.list_tools()
        print(f"[MCP Client] Successfully discovered {len(self.cached_tools)} MCP tools:")
        for tool in self.cached_tools:
            print(f"  - {tool['name']}: {tool['description'][:60]}...")

    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Returns raw MCP tool definitions list.
        """
        return self.cached_tools

    def get_llm_function_declarations(self) -> List[Dict[str, Any]]:
        """
        Formats MCP tools into Gemini / OpenAI JSON function declarations for LLM context injection.
        """
        declarations = []
        for tool in self.cached_tools:
            declarations.append({
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["inputSchema"]
            })
        return declarations

    def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invokes tool execution over MCP Client -> Server interface.
        """
        print(f"[MCP Client] Sending call_tool request to MCP Server -> '{tool_name}'")
        response = self.connected_server.call_tool(tool_name, arguments)
        print(f"[MCP Client] Received tool response from MCP Server: {response.get('status')}")
        return response

mcp_client = GuardianMCPClient()
