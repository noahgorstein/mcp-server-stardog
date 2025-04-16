import httpx
import base64
import logging


from .services import DatabaseService, SecurityService, MonitoringService, QueryService
from .errors import StardogClientError

logger = logging.getLogger("mcp_server_stardog")


class StardogClient:
    """
    A client for interacting with the Stardog server.
    """

    def __init__(
        self,
        endpoint: str,
        username: str | None = None,
        password: str | None = None,
        auth_token: str | None = None,
    ):
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.auth_token = auth_token
        self._validate_auth()

        self._database = DatabaseService(self)
        self._security = SecurityService(self)
        self._monitoring = MonitoringService(self)
        self._query = QueryService(self)

    @property
    def database(self) -> DatabaseService:
        """
        Access the database service.
        """
        return self._database

    @property
    def security(self) -> SecurityService:
        """
        Access the security service.
        """
        return self._security

    @property
    def monitoring(self) -> MonitoringService:
        """
        Access the monitoring service.
        """
        return self._monitoring

    @property
    def query(self) -> QueryService:
        """
        Access the query service.
        """
        return self._query

    def _validate_auth(self) -> None:
        if (not self.username or not self.password) and not self.auth_token:
            raise ValueError("No authentication credentials provided.")

    def get_auth(self) -> tuple[str, str] | str:
        """
        Get the authentication credentials for the Stardog database client.
        """
        if self.auth_token:
            return self.auth_token
        return self.username, self.password

    def _get_base_headers(self) -> dict[str, str]:
        """
        Get the headers for the Stardog API request.
        """
        headers = {}
        auth = self.get_auth()
        if isinstance(auth, tuple):
            username, password = auth
            b64_encoded_bytes = base64.b64encode(f"{username}:{password}".encode())
            headers["Authorization"] = f"Basic {b64_encoded_bytes.decode()}"
        else:
            headers["Authorization"] = f"Bearer {auth}"
        return headers

    async def _request(
        self,
        method: str,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Generalized method to make HTTP requests to the Stardog API.
        """
        try:
            async with httpx.AsyncClient() as client:
                base_headers = self._get_base_headers()
                if headers:
                    headers.update(base_headers)
                else:
                    headers = base_headers

                # Dynamically call the appropriate HTTP method
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=params,
                    **kwargs,
                )
                response.raise_for_status()
                return response
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error during {method.upper()} request to {url}: {e.response.text}"
            )
            raise StardogClientError(
                message=f"HTTP error occurred during {method.upper()} request.",
                url=url,
                status_code=e.response.status_code,
                details=e.response.text,
            ) from e
        except Exception as e:
            logger.error(
                f"Unexpected error during {method.upper()} request to {url}: {e}"
            )
            raise StardogClientError(
                message=f"Unexpected error occurred during {method.upper()} request.",
                url=url,
                details=str(e),
            ) from e

    async def _get(
        self, url: str, headers: dict | None = None, params: dict | None = None
    ) -> httpx.Response:
        """
        Make a GET request to the Stardog API.
        """
        return await self._request("GET", url, headers=headers, params=params)

    async def _post(
        self, url: str, headers: dict | None = None, **kwargs
    ) -> httpx.Response:
        """
        Make a POST request to the Stardog API.
        """
        return await self._request("POST", url, headers=headers, **kwargs)

    async def _put(
        self, url: str, headers: dict | None = None, **kwargs
    ) -> httpx.Response:
        """
        Make a PUT request to the Stardog API.
        """
        return await self._request("PUT", url, headers=headers, **kwargs)

    async def _delete(
        self, url: str, headers: dict | None = None, **kwargs
    ) -> httpx.Response:
        """
        Make a DELETE request to the Stardog API.
        """
        return await self._request("DELETE", url, headers=headers, **kwargs)
