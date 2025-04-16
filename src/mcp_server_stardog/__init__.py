from . import server
import asyncio
import click
import logging

logger = logging.getLogger("mcp_server_stardog")
logging.basicConfig(level=logging.INFO, format="[%(name)s] %(levelname)s - %(message)s")


@click.command()
@click.option(
    "-e",
    "--endpoint",
    envvar="SD_ENDPOINT",
    help="Stardog endpoint URL. The environment variable SD_ENDPOINT will be used if not provided.",
    required=True,
)
@click.option(
    "-u",
    "--username",
    envvar="SD_USERNAME",
    help="Stardog username. The environment variable SD_USERNAME will be used if not provided.",
)
@click.option(
    "-p",
    "--password",
    envvar="SD_PASSWORD",
    help="Stardog password. The environment variable SD_PASSWORD will be used if not provided.",
)
@click.option(
    "-t",
    "--auth-token",
    envvar="SD_AUTH_TOKEN",
    help="Stardog authentication token. The environment variable SD_AUTH_TOKEN will be used if not provided.",
)
def main(endpoint: str, username: str, password: str, auth_token: str):
    """
    Start the Stardog MCP server. You can authenticate using either a username and password or an authentication token.
    If both are provided, the authentication token will be used.
    """

    asyncio.run(
        server.main(
            endpoint=endpoint,
            username=username,
            password=password,
            auth_token=auth_token,
        )
    )


__all__ = ["main", "server"]
