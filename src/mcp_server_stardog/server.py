from mcp.server import InitializationOptions, NotificationOptions, Server
import mcp.server.stdio
import mcp.types as types
import logging
from .stardog_client import StardogClient
from .tools import ToolHandler
from .prompts import PromptHandler

from pydantic import AnyUrl


SERVER_VERSION = "0.0.1"

logger = logging.getLogger("mcp_server_stardog")


async def main(
    endpoint: str, username: str | None, password: str | None, auth_token: str | None
):
    logger.info("Starting Stardog MCP server ⭐🐕")
    server = Server("mcp-stardog-server")
    sd_client = StardogClient(
        endpoint=endpoint, username=username, password=password, auth_token=auth_token
    )
    logger.info("Registering handlers")
    tool_handler = ToolHandler(sd_client)
    prompt_handler = PromptHandler(sd_client)

    @server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        """
        List available resources.
        """
        logger.info("No resources available to list.")
        return []

    @server.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> str:
        """
        Read a resource by its URI.
        """
        logger.info(f"Reading resource: {uri}")
        raise ValueError("Unsupported URI scheme: {uri.scheme}")

    @server.get_prompt()
    async def handle_get_prompt(
        name: str, arguments: dict[str, str] | None
    ) -> types.GetPromptResult:
        """
        Generate a prompt by combining arguments with the server state.
        """
        return await prompt_handler.handle_get_prompt(name, arguments)

    @server.list_prompts()
    async def handle_list_prompts() -> list[types.Prompt]:
        """
        List all available prompts.
        Prompts can be used to generate text based on the server state.
        """
        return await prompt_handler.list_prompts()

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """
        List all tools in the MCP server.
        Each tool specifies its arguments using JSON Schema validation.
        """
        return await tool_handler.handle_list_tools()

    @server.call_tool()
    async def handle_tool_call(
        name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        Handle tool execution requests.
        Tools can modify the server state and notify clients of changes.
        """
        return await tool_handler.handle_tool_call(name, arguments)

    # run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="stardog",
                server_version=SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

        logger.info("\n Stardog MCP Server shutting down...")
