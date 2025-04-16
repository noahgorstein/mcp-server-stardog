import logging

from mcp_server_stardog.errors import PromptError
from .stardog_client import StardogClient
from mcp.types import (
    Prompt,
    PromptArgument,
    GetPromptResult,
    PromptMessage,
    TextContent,
)
from .errors import StardogClientError

logger = logging.getLogger("mcp_server_stardog")

DB_CONFIG_INFO_TEMPLATE = """
Analyze the Stardog database configuration for database '{database_name}' and create a comprehensive report.

First, review this documentation:
{filtered_option_docs}

Then, analyze these specific configuration options: {option_keys}

Current configuration values:
{options}

Create a detailed report with:
1. A brief introduction identifying the database and the options being analyzed
2. A complete markdown table with these exact columns:
   - Label
   - Name
   - Value
   - Description (explain what each setting controls)
   - Category (the configuration category this belongs to)
   - Default Value (what the system sets if not specified)
   - Type (data type)
   - Mutable (can it be changed after database creation)
   - Mutable While Online (can it be changed without taking the database offline)
3. For each option, compare the current value with documentation to provide context about its significance
4. Highlight any values that differ from defaults and explain potential impacts

Format the table professionally with proper markdown syntax and alignment.
"""

ROLES_SUMMARY_TEMPLATE = """
Below are the roles and their permissions in the Stardog server in JSON format.

{roles_with_permissions}

This is example output from the Stardog CLI when requesting permissions for 1 role. 

+---------------+---------------+-------------+
| Resource Type | Resource Name | Permissions |
+---------------+---------------+-------------+
| db            | *             | --R----     |
| metadata      | *             | --R----     |
+---------------+---------------+-------------+

Provide a similar table but in markdown for all roles and their permissions mentioned above.

Do not mention anything about the example output. Just provide the table with the roles and their permissions and a summary of the permissions.

Here is some information about the permissions:

- Action types include: "read" "write" "create" "delete" "revoke" "grant" "execute" "all"
 - Resource types include: "ALL" "USER" "ROLE" "ROLE_ASSIGNMENT" "PERMISSION" "DATABASE" "NAMED_GRAPH" "DATA_SOURCE" "VIRTUAL_GRAPH" "DBMS_ADMIN" "DATABASE_METADATA" "DATABASE_ADMIN" "STORED_QUERY" "CACHE" "CACHE_TARGET" "SENSITIVE_PROPERTIES" "ENTITY_RESOLUTION"
- Resource names depend on the resource type but * is a wildcard for all resources of that type.
"""


class PromptHandler:
    """
    Handles the generation of prompts for the server.
    """

    PROMPTS_METADATA = {
        "database_config_helper": {
            "description": "Get the configuration of a Stardog database.",
            "arguments": [
                PromptArgument(
                    name="database_name",
                    description="Name of the Stardog database.",
                    required=True,
                ),
                PromptArgument(
                    name="option_keys",
                    description="List of specific database option keys (e.g. 'search.enabled') to filter the configuration.",
                    required=True,
                ),
            ],
        },
        "roles_summary": {
            "description": "Get a summary of roles in the Stardog server.",
            "arguments": [],
        },
    }

    def __init__(self, sd_client: StardogClient):
        self.sd_client = sd_client
        self.prompt_dispatcher = {
            "database_config_helper": self._handle_database_config_helper,
            "roles_summary": self._handle_roles_summary,
        }

    async def handle_get_prompt(self, name: str, arguments: dict[str, str]) -> str:
        """
        Handle the generation of a specific prompt based on its name.
        """
        if name not in self.prompt_dispatcher:
            raise ValueError(f"Unknown prompt name: {name}")
        try:
            formatted_prompt = await self.prompt_dispatcher[name](arguments)
            description = self.PROMPTS_METADATA[name]["description"]
            return GetPromptResult(
                description=description,
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=formatted_prompt),
                    )
                ],
            )
        except StardogClientError as e:
            logger.error(
                f"Stardog client error occurred while generating prompt: {e}",
                exc_info=True,
            )
            raise PromptError(name=name, message=str(e)) from e
        except Exception as e:
            logger.error(
                f"Unexpected error while generating prompt {name}: {e}",
                exc_info=True,
            )
            raise PromptError(name=name, message=str(e)) from e

    async def _handle_database_config_helper(self, arguments: dict[str, str]) -> str:
        """
        Handle the 'database_config_helper' prompt.
        """
        database_name = arguments.get("database_name")
        option_keys = [
            arg.strip() for arg in arguments.get("option_keys", "").split(",")
        ]

        if not database_name:
            raise ValueError("database_name is required.")
        if not option_keys:
            raise ValueError("option_keys is required.")

        option_docs = await self.sd_client.database.get_configuration_documentation()
        filtered_option_docs = "\n".join(
            f"{key}: {value}"
            for key, value in option_docs.items()
            if option_keys and key in option_keys
        )
        options = await self.sd_client.database.get_configuration(
            database_name, option_keys
        )
        return DB_CONFIG_INFO_TEMPLATE.format(
            filtered_option_docs=filtered_option_docs,
            database_name=database_name,
            option_keys=option_keys,
            options=options,
        )

    async def _handle_roles_summary(self, arguments: dict[str, str]) -> str:
        """
        Handle the 'roles_summary' prompt.
        """
        roles_with_permissions = (
            await self.sd_client.security.list_roles_with_permissions()
        )
        return ROLES_SUMMARY_TEMPLATE.format(
            roles_with_permissions=roles_with_permissions
        )

    async def list_prompts(self) -> list[Prompt]:
        """
        List all available prompts with their descriptions and arguments.
        """
        return [
            Prompt(
                name=name,
                description=metadata["description"],
                arguments=metadata.get("arguments", []),
            )
            for name, metadata in self.PROMPTS_METADATA.items()
        ]
