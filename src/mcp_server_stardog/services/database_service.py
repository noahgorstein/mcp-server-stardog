from __future__ import annotations
from typing import TYPE_CHECKING
import logging


if TYPE_CHECKING:
    from ..stardog_client import StardogClient

logger = logging.getLogger("mcp_server_stardog")


class DatabaseService:
    """
    Handles database-related operations in Stardog.
    """

    def __init__(self, client: StardogClient):
        self.client = client

    async def list(self) -> list[str]:
        """
        Get the list of databases from Stardog.
        """
        url = f"{self.client.endpoint}/admin/databases"
        response = await self.client._get(url, None)
        data = response.json()
        return data.get("databases", [])

    async def size(self, database_name: str) -> int:
        """
        Get the estimated size of a Stardog database in triples.
        """
        url = f"{self.client.endpoint}/{database_name}/size"
        response = await self.client._get(url, None)
        triples = int(response.text)
        return triples

    async def get_configuration(
        self, database_name: str, option_keys: list[str] | None = None
    ) -> dict:
        """
        Get the configuration of a Stardog database. Optionally filter by specific keys.
        """
        url = f"{self.client.endpoint}/admin/databases/{database_name}/options"
        response = await self.client._get(url, None)
        data = response.json()
        if option_keys:
            return {key: data.get(key, "not_found") for key in option_keys}
        return data

    async def get_configuration_documentation(self) -> dict:
        """
        Get the configuration documentation for a Stardog database.
        """
        url = f"{self.client.endpoint}/admin/config_properties"
        response = await self.client._get(url, None)
        return response.json()
