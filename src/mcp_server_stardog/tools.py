import logging
from mcp.types import TextContent, Tool

from mcp_server_stardog.errors import ToolError
from mcp_server_stardog.services.security_service import Permission
from .stardog_client import StardogClient
from .errors import StardogClientError

logger = logging.getLogger("mcp_server_stardog")


class ToolHandler:
    def __init__(self, sd_client: StardogClient):
        self.sd_client = sd_client
        self.tool_dispatch = {
            "assign_permission_to_role": self.handle_assign_permission_to_role,
            "assign_permission_to_user": self.handle_assign_permission_to_user,
            "assign_role_to_user": self.handle_assign_role_to_user,
            "create_role": self.handle_create_role,
            "delete_role": self.handle_delete_role,
            "execute_sparql_read": self.handle_execute_sparql_read,
            "get_database_configuration": self.handle_get_database_configuration,
            "get_database_configuration_documentation": self.handle_get_database_configuration_documentation,
            "get_database_size": self.handle_get_database_size,
            "get_roles_assigned_to_user": self.handle_get_roles_assigned_to_user,
            "get_server_metrics": self.handle_get_server_metrics,
            "get_users_with_role": self.handle_get_users_with_role,
            "get_whoami": self.handle_get_whoami,
            "kill_process": self.handle_kill_process,
            "list_databases": self.handle_list_databases,
            "list_processes": self.handle_list_processes,
            "list_roles": self.handle_list_roles,
            "list_users": self.handle_list_users,
            "list_stored_queries": self.handle_list_stored_queries,
            "revoke_permission_from_role": self.handle_revoke_permission_from_role,
            "revoke_permission_from_user": self.handle_revoke_permission_from_user,
            "revoke_role_from_user": self.handle_revoke_role_from_user,
        }

    async def handle_list_tools(self) -> list[Tool]:
        """
        Dynamically generate a list of tools based on the tool_dispatch dictionary.
        """
        return [
            Tool(
                name=tool_name,
                description=self.get_tool_description(tool_name),
                inputSchema=self.get_tool_input_schema(tool_name),
            )
            for tool_name in self.tool_dispatch.keys()
        ]

    def get_tool_description(self, tool_name: str) -> str:
        """
        Return a description for the given tool.
        """
        descriptions = {
            "assign_permission_to_role": "Assign a permission to a specific role.",
            "assign_permission_to_user": "Assign a permission to a specific user.",
            "assign_role_to_user": "Assign a role to a specific user.",
            "create_role": "Create a new role in the Stardog server.",
            "delete_role": "Delete a role from the Stardog server. Optionally force delete the role, deleting the role while it is assigned to other users.",
            "execute_sparql_read": "Execute a SPARQL read query against a Stardog database. SELECT, ASK, CONSTRUCT, and DESCRIBE queries are supported.",
            "get_database_configuration": "Get the configuration of a Stardog database. Optionally filter by specific keys.",
            "get_database_configuration_documentation": "Get documentation for Stardog database configuration options.",
            "get_database_size": "Get the estimated size of a Stardog database in triples.",
            "get_roles_assigned_to_user": "Get the names of roles assigned to a specific user.",
            "get_server_metrics": "Get the server metrics from Stardog.",
            "get_users_with_role": "Get all the usernames of users assigned to a specific role.",
            "get_whoami": "Return the authenticated user's username.",
            "kill_process": "Kill a specific process on the Stardog server.",
            "list_databases": "List the names of all Stardog databases in the Stardog server.",
            "list_processes": "List all the processes on the Stardog server.",
            "list_roles": "List all of the roles names in the Stardog server. Optionally include role permissions. Optionally filter by specific role names.",
            "list_users": "List all users in the Stardog server. Optionally include details about users like permissions, superuser status and whether they are enabled. Optionally filter by specific usernames.",
            "list_stored_queries": "List all stored queries in the Stardog server.",
            "revoke_permission_from_role": "Revoke a permission from a specific role.",
            "revoke_permission_from_user": "Revoke a permission from a specific user.",
            "revoke_role_from_user": "Revoke a role from a specific user.",
        }
        return descriptions.get(tool_name, "No description available.")

    def get_tool_input_schema(self, tool_name: str) -> dict:
        """
        Return the input schema for the given tool.
        """
        schemas = {
            "assign_permission_to_role": {
                "type": "object",
                "properties": {
                    "role_name": {
                        "type": "string",
                        "description": "Name of the role.",
                    },
                    "permission": Permission.model_json_schema(),
                },
                "required": ["role_name", "permission"],
            },
            "assign_permission_to_user": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Name of the user.",
                    },
                    "permission": Permission.model_json_schema(),
                },
                "required": ["username", "permission"],
            },
            "assign_role_to_user": {
                "type": "object",
                "properties": {
                    "role_name": {
                        "type": "string",
                        "description": "Name of the role.",
                    },
                    "username": {
                        "type": "string",
                        "description": "Username of the user.",
                    },
                },
                "required": ["role_name", "username"],
            },
            "create_role": {
                "type": "object",
                "properties": {
                    "role_name": {
                        "type": "string",
                        "description": "Name of the role to create.",
                    },
                },
                "required": ["role_name"],
            },
            "delete_role": {
                "type": "object",
                "properties": {
                    "role_name": {
                        "type": "string",
                        "description": "Name of the role to delete.",
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Whether to force delete the role even if it is assigned to users.",
                        "default": False,
                    },
                },
                "required": ["role_name"],
            },
            "execute_sparql_read": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SPARQL query to execute.",
                    },
                    "database": {
                        "type": "string",
                        "description": "Name of the Stardog database to execute the query against.",
                    },
                    "query_type": {
                        "type": "string",
                        "description": "Type of the SPARQL query (SELECT, ASK, CONSTRUCT, DESCRIBE).",
                        "enum": ["SELECT", "ASK", "CONSTRUCT", "DESCRIBE"],
                        "default": "SELECT",
                    },
                    "reasoning": {
                        "type": "boolean",
                        "description": "Whether to use reasoning for the query.",
                        "default": False,
                    },
                    "schema": {
                        "type": "string",
                        "description": "The reasoning schema to use for the query.",
                        "default": "default",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return.",
                        "default": 1000,
                    },
                    "timeout_ms": {
                        "type": "integer",
                        "description": "Timeout for the query in milliseconds.",
                        "default": 30000,
                    },
                },
                "required": ["query", "database"],
            },
            "get_database_configuration": {
                "type": "object",
                "properties": {
                    "database_name": {
                        "type": "string",
                        "description": "Name of the Stardog database.",
                    },
                    "option_keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of specific database option keys to filter the configuration.",
                    },
                },
                "required": ["database_name"],
            },
            "get_database_configuration_documentation": {
                "type": "object",
            },
            "get_database_size": {
                "type": "object",
                "properties": {
                    "database_name": {
                        "type": "string",
                        "description": "Name of the Stardog database.",
                    },
                },
                "required": ["database_name"],
            },
            "get_roles_assigned_to_user": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username of the user.",
                    },
                },
                "required": ["username"],
            },
            "get_server_metrics": {
                "type": "object",
            },
            "get_users_with_role": {
                "type": "object",
                "properties": {
                    "role_name": {
                        "type": "string",
                        "description": "Name of the role.",
                    },
                },
                "required": ["role_name"],
            },
            "get_whoami": {
                "type": "object",
            },
            "kill_process": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID of the process to kill.",
                    },
                },
                "required": ["id"],
            },
            "list_databases": {
                "type": "object",
            },
            "list_processes": {
                "type": "object",
            },
            "list_roles": {
                "type": "object",
                "properties": {
                    "include_permissions": {
                        "type": "boolean",
                        "description": "Whether to include permissions assigned to the roles.",
                        "default": False,
                    },
                    "roles_filter": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of role names to filter the results. Only roles with these names will be included.",
                        "default": [],
                    },
                },
            },
            "list_users": {
                "type": "object",
                "properties": {
                    "include_details": {
                        "type": "boolean",
                        "description": "Whether to include detailed information about users.",
                        "default": False,
                    },
                    "usernames_filter": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of usernames to filter the results. Only users with these usernames will be included.",
                        "default": [],
                    },
                },
            },
            "list_stored_queries": {
                "type": "object",
            },
            "revoke_permission_from_role": {
                "type": "object",
                "properties": {
                    "role_name": {
                        "type": "string",
                        "description": "Name of the role.",
                    },
                    "permission": Permission.model_json_schema(),
                },
                "required": ["role_name", "permission"],
            },
            "revoke_permission_from_user": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Name of the user.",
                    },
                    "permission": Permission.model_json_schema(),
                },
                "required": ["username", "permission"],
            },
            "revoke_role_from_user": {
                "type": "object",
                "properties": {
                    "role_name": {
                        "type": "string",
                        "description": "Name of the role.",
                    },
                    "username": {
                        "type": "string",
                        "description": "Username of the user.",
                    },
                },
                "required": ["role_name", "username"],
            },
        }

        return schemas.get(tool_name, {"type": "object"})

    async def handle_tool_call(
        self, name: str, arguments: dict | None
    ) -> list[TextContent]:
        """
        Handle tool execution requests using the dispatch table.
        """
        logger.info(f"Calling tool: {name}::{arguments}")
        arguments = arguments or {}

        handler = self.tool_dispatch.get(name)
        if not handler:
            return [TextContent(type="text", text=f"Unsupported tool: {name}")]

        try:
            return await handler(arguments)
        except StardogClientError as e:
            logger.error(
                f"Stardog client error occurred while executing tool: {e}",
                exc_info=True,
            )
            raise ToolError(name=name, message=str(e)) from e
        except Exception as e:
            logger.error(
                f"Unexpected error while executing tool {name}: {e}",
                exc_info=True,
            )
            raise ToolError(name=name, message=str(e)) from e

    async def handle_list_databases(self, arguments: dict) -> list[TextContent]:
        tool_response = await self.sd_client.database.list()
        return [TextContent(type="text", text=str(tool_response))]

    async def handle_get_database_size(self, arguments: dict) -> list[TextContent]:
        database_name = arguments.get("database_name")
        if not database_name:
            return [TextContent(type="text", text="Error: database_name is required.")]
        tool_response = await self.sd_client.database.size(database_name)
        return [TextContent(type="text", text=str(tool_response))]

    async def handle_get_database_configuration(
        self, arguments: dict
    ) -> list[TextContent]:
        database_name = arguments.get("database_name")
        option_keys = arguments.get("option_keys")
        if not database_name:
            return [TextContent(type="text", text="Error: database_name is required.")]
        tool_response = await self.sd_client.database.get_configuration(
            database_name, option_keys
        )
        return [TextContent(type="text", text=str(tool_response))]

    async def handle_get_database_configuration_documentation(
        self, arguments: dict
    ) -> list[TextContent]:
        tool_response = await self.sd_client.database.get_configuration_documentation()
        return [TextContent(type="text", text=str(tool_response))]

    async def handle_list_roles(self, arguments: dict) -> list[TextContent]:
        include_permissions = arguments.get("include_permissions", False)
        roles_filter = arguments.get("roles_filter", [])

        if not include_permissions:
            tool_response = await self.sd_client.security.list_roles()
            return [TextContent(type="text", text=str(tool_response))]

        data = await self.sd_client.security.list_roles_with_permissions()
        roles = data["roles"]
        if roles_filter:
            roles = [role for role in roles if role["rolename"] in roles_filter]
        return [TextContent(type="text", text=str(roles))]

    async def handle_get_users_with_role(self, arguments: dict) -> list[TextContent]:
        role_name = arguments.get("role_name")
        if not role_name:
            return [TextContent(type="text", text="Error: role_name is required.")]
        tool_response = await self.sd_client.security.get_users_with_role(role_name)
        return [TextContent(type="text", text=str(tool_response))]

    async def handle_list_users(self, arguments: dict) -> list[TextContent]:
        include_details = arguments.get("include_details", False)
        usernames_filter = arguments.get("usernames_filter", [])

        if not include_details:
            tool_response = await self.sd_client.security.list_users()
            return [TextContent(type="text", text=str(tool_response))]

        data = await self.sd_client.security.get_users_with_details()
        users = data["users"]
        if usernames_filter:
            users = [user for user in users if user["username"] in usernames_filter]

        return [TextContent(type="text", text=str(users))]

    async def handle_get_roles_assigned_to_user(
        self, arguments: dict
    ) -> list[TextContent]:
        username = arguments.get("username")
        if not username:
            return [TextContent(type="text", text="Error: username is required.")]
        tool_response = await self.sd_client.security.get_roles_assigned_to_user(
            username
        )
        return [TextContent(type="text", text=str(tool_response))]

    async def handle_get_whoami(self, arguments: dict) -> list[TextContent]:
        tool_response = await self.sd_client.security.get_whoami()
        return [TextContent(type="text", text=str(tool_response))]

    async def handle_create_role(self, arguments: dict) -> list[TextContent]:
        role_name = arguments.get("role_name")
        if not role_name:
            return [TextContent(type="text", text="Error: role_name is required.")]
        await self.sd_client.security.create_role(role_name)
        return [
            TextContent(type="text", text=f"Role '{role_name}' created successfully.")
        ]

    async def handle_delete_role(self, arguments: dict) -> list[TextContent]:
        role_name = arguments.get("role_name")
        force = arguments.get("force", False)
        if not role_name:
            return [TextContent(type="text", text="Error: role_name is required.")]
        await self.sd_client.security.delete_role(role_name, force)
        return [
            TextContent(type="text", text=f"Role '{role_name}' deleted successfully.")
        ]

    async def handle_assign_role_to_user(self, arguments: dict) -> list[TextContent]:
        role_name = arguments.get("role_name")
        username = arguments.get("username")
        if not role_name or not username:
            return [
                TextContent(
                    type="text", text="Error: role_name and username are required."
                )
            ]
        await self.sd_client.security.assign_role_to_user(role_name, username)
        return [
            TextContent(
                type="text",
                text=f"Successfully assigned role '{role_name}' to user '{username}'.",
            )
        ]

    async def handle_revoke_role_from_user(self, arguments: dict) -> list[TextContent]:
        role_name = arguments.get("role_name")
        username = arguments.get("username")
        if not role_name or not username:
            return [
                TextContent(
                    type="text", text="Error: role_name and username are required."
                )
            ]
        await self.sd_client.security.revoke_role_from_user(role_name, username)
        return [
            TextContent(
                type="text",
                text=f"Successfully revoked role '{role_name}' from user '{username}'.",
            )
        ]

    async def handle_assign_permission_to_role(self, arguments: dict):
        role_name = arguments.get("role_name")
        permission = arguments.get("permission")
        if not role_name or not permission:
            return [
                TextContent(
                    type="text", text="Error: role_name and permission are required."
                )
            ]
        permission = Permission(**permission)
        await self.sd_client.security.assign_permission_to_role(role_name, permission)
        return [
            TextContent(
                type="text",
                text=f"Successfully assigned permission to role '{role_name}'.",
            )
        ]

    async def handle_revoke_permission_from_role(self, arguments: dict):
        role_name = arguments.get("role_name")
        permission = arguments.get("permission")
        if not role_name or not permission:
            return [
                TextContent(
                    type="text", text="Error: role_name and permission are required."
                )
            ]
        permission = Permission(**permission)
        await self.sd_client.security.revoke_permission_from_role(role_name, permission)
        return [
            TextContent(
                type="text",
                text=f"Successfully revoked permission from role '{role_name}'.",
            )
        ]

    async def handle_revoke_permission_from_user(self, arguments: dict):
        username = arguments.get("username")
        permission = arguments.get("permission")
        if not username or not permission:
            return [
                TextContent(
                    type="text", text="Error: username and permission are required."
                )
            ]
        permission = Permission(**permission)
        await self.sd_client.security.revoke_permission_from_user(username, permission)
        return [
            TextContent(
                type="text",
                text=f"Successfully revoked permission from user '{username}'.",
            )
        ]

    async def handle_assign_permission_to_user(self, arguments: dict):
        username = arguments.get("username")
        permission = arguments.get("permission")
        if not username or not permission:
            return [
                TextContent(
                    type="text", text="Error: username and permission are required."
                )
            ]
        permission = Permission(**permission)
        await self.sd_client.security.assign_permission_to_user(username, permission)
        return [
            TextContent(
                type="text",
                text=f"Successfully assigned permission to user '{username}'.",
            )
        ]

    async def handle_list_processes(self, arguments: dict) -> list[TextContent]:
        tool_response = await self.sd_client.monitoring.list_processes()
        return [TextContent(type="text", text=str(tool_response))]

    async def handle_kill_process(self, arguments: dict) -> list[TextContent]:
        process_id = arguments.get("id")
        if not process_id:
            return [TextContent(type="text", text="Error: id is required.")]
        await self.sd_client.monitoring.kill_process(process_id)
        return [
            TextContent(type="text", text=f"Process with ID '{process_id}' killed.")
        ]

    async def handle_get_server_metrics(self, arguments: dict) -> list[TextContent]:
        metrics = await self.sd_client.monitoring.get_server_metrics()
        return [TextContent(type="text", text=str(metrics))]

    async def handle_list_stored_queries(self, arguments: dict) -> list[TextContent]:
        tool_response = await self.sd_client.query.list_stored()
        return [TextContent(type="text", text=str(tool_response))]

    async def handle_execute_sparql_read(self, arguments: dict) -> list[TextContent]:
        query = arguments.get("query")
        database = arguments.get("database")
        query_type = arguments.get("query_type", "SELECT")
        schema = arguments.get("schema", "default")
        timeout_ms = arguments.get("timeout_ms", 30000)
        limit = arguments.get("limit", 1000)
        reasoning = arguments.get("reasoning", False)

        if not query:
            return [TextContent(type="text", text="Error: query is required.")]

        if not database:
            return [TextContent(type="text", text="Error: database is required.")]
        tool_response = await self.sd_client.query.sparql_read(
            database,
            query,
            query_type=query_type,
            schema=schema,
            reasoning=reasoning,
            limit=limit,
            timeout_ms=timeout_ms,
        )
        return [TextContent(type="text", text=str(tool_response))]
