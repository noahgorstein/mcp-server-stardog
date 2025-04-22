from __future__ import annotations
from typing import TYPE_CHECKING
import logging


if TYPE_CHECKING:
    from ..stardog_client import StardogClient

logger = logging.getLogger("mcp_server_stardog")


class MonitoringService:
    """
    Handles monitoring-related operations in Stardog.
    """

    def __init__(self, client: StardogClient):
        self.client = client

    async def list_processes(self) -> dict:
        """
        Get the list of processes from Stardog.
        """
        url = f"{self.client.endpoint}/admin/processes"
        response = await self.client._get(url, None)
        return response.json()

    async def kill_process(self, id: int) -> None:
        """
        Kill a specific process in Stardog.
        """
        url = f"{self.client.endpoint}/admin/processes/{id}"
        await self.client._delete(url, None)
        return None

    async def get_server_metrics(self) -> dict:
        """
        Get server metrics from Stardog.
        """
        url = f"{self.client.endpoint}/admin/status"
        response = await self.client._get(url, None)
        return response.json()
