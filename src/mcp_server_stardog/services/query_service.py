from __future__ import annotations
from typing import TYPE_CHECKING, Literal
import logging


if TYPE_CHECKING:
    from ..stardog_client import StardogClient

logger = logging.getLogger("mcp_server_stardog")


class QueryService:
    """
    Handles query-related operations in Stardog.
    """

    def __init__(self, client: StardogClient):
        self.client = client

    async def list_stored(self) -> list[str]:
        """
        Get the list of stored queries from Stardog.
        """
        url = f"{self.client.endpoint}/admin/queries/stored"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        # need to specify JSON cause default is turtle serialization
        response = await self.client._get(url, headers=headers)
        return response.json()

    async def sparql_read(
        self,
        database: str,
        query: str,
        query_type: Literal["select", "construct", "ask", "describe"] = "select",
        reasoning: bool = False,
        schema: str = "default",
        limit: int = 1000,
        timeout_ms: int = 30000,
    ) -> str | bytes:
        """
        Execute a SPARQL read query against a Stardog database.

        Returns:
            JSON (as a string) for 'select' and 'ask' queries.
            Raw bytes for 'construct' and 'describe' queries.
        """
        url = f"{self.client.endpoint}/{database}/query"

        match query_type.lower():
            case "select" | "ask":
                accept_header = "application/sparql-results+json"
            case "construct" | "describe":
                accept_header = "text/turtle"
            case _:
                raise ValueError(
                    f"Invalid query type: {query_type}. Must be one of 'select', 'construct', 'ask', or 'describe'."
                )

        headers = {
            "Accept": accept_header,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "reasoning": reasoning,
            "schema": schema,
            "limit": limit,
            "timeout": timeout_ms,
        }
        data = {"query": query}
        response = await self.client._post(
            url, headers=headers, params=params, data=data
        )

        if query_type in {"select", "ask"}:
            return response.json()
        return response.content

    