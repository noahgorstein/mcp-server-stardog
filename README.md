# Stardog MCP Server

An [MCP server](https://modelcontextprotocol.io/introduction) implementation that interacts with a Stardog server's APIs, enabling automation
and interaction capabilities for developers and tools.

https://github.com/user-attachments/assets/4a41d6fb-8b20-4994-b973-81ce1c10c04a

> [!WARNING]
> This is a work in progress and is subject to change quite drastically.

> [!CAUTION]
> Be careful when using any MCP server. This MCP server will make requests to the Stardog server and may modify data or configurations. If you want to limit mutating any data, you could provide credentials to a read-only user or with limited permissions.

## Getting Started

Clone the repository to your local machine. Make note of the path to the cloned repository, as you will need it later.

```bash

$ pwd
/Users/noah/projects/mcp-server-stardog
```

### General Prerequisites

- [`uv`](https://docs.astral.sh/uv/) installed.

> [!NOTE]
> If you plan to use the MCP with Claude Desktop or any other MCP comptaible client, the client needs to be installed.

### Stardog Prerequisites

You will need credentials to access a running Stardog server.

```bash
$ curl -i -u anonymous:anonymous https://express.stardog.cloud:5820/admin/status/whoami
HTTP/2 200
date: Wed, 16 Apr 2025 20:46:50 GMT
content-length: 9

anonymous
```

### Usage with VS Code

Add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` and typing `Preferences: Open User Settings (JSON)`.

```json
 "mcp": {
        "servers": {
            "stardog": {
                "type": "stdio",
                "command": "uv",
                "args": [
                    "--directory",
                    "/Users/noah/projects/mcp-server-stardog",
                    "run",
                    "mcp-server-stardog"
                ],
                "env": {
                    "SD_USERNAME": "${env:SD_USERNAME}",
                    "SD_PASSWORD": "${env:SD_PASSWORD}",
                    "SD_ENDPOINT": "${env:SD_ENDPOINT}"
                },
            }
        }
    }
```

You will want to provide the path to where this repository is cloned for the `--directory` option to `uv`. VS Code will sub in `SD_USERNAME`, `SD_PASSWORD`, and `SD_ENDPOINT` environment variables which the MCP server will use. Once you set these environment variables, you may need to restart VS Code to pick up the environment variables.

> [!NOTE]
> More about using MCP server tools in VS Code's [agent mode documentation](https://code.visualstudio.com/docs/copilot/chat/mcp-servers).

You can also use the `--endpoint`, `--username`, and `--password` command line options to set the values directly in the configuration.

```json
 "mcp": {
        "servers": {
            "stardog": {
                "type": "stdio",
                "command": "uv",
                "args": [
                    "--directory",
                    "/Users/noah/projects/mcp-server-stardog",
                    "run",
                    "mcp-server-stardog",
                    "--endpoint",
                    "https://express.stardog.cloud:5820",
                    "--username",
                    "anonymous",
                    "--password",
                    "anonymous"
                ]
            }
        }
    }
```

> [!NOTE]
> You can also use a token to authenticate with the Stardog server. You can set the token in the `SD_AUTH_TOKEN` environment variable or use the `--auth-token` command line argument. The token will be used instead of the username and password if both are provided.


### Usage with Claude Desktop

1. Install Claude Desktop from [https://claude.ai/download](https://claude.ai/download) if you haven't already.
2. Open the Claude Desktop configuration file.
    - To quickly access it or create it the first time, open the Claude Desktop app, select **Settings**, and click on the **Developer** tab. Finally, click on the **Edit Config** button.
    - Add the following configuration to the file, substituting the values for `username`, `password`, and `endpoint` with your own:

```json
{
    "mcpServers": {
        "stardog": {
            "command": "/Users/noah/.local/bin/uv",
            "args": [
                "--directory",
		"/Users/noah/projects/mcp-server-stardog",
                "run",
                "mcp-server-stardog"
                "--endpoint",
                "https://express.stardog.cloud:5820",
                "--username",
                "anonymous",
                "--password",
                "anonymous",
                "--auth-token",
                "your_auth_token"
            ],
        }
    }
}
```

> [!NOTE]
> You can authenticate to Stardog using either a username and password or an authentication token. If you provide both, the authentication token will be used. The `username`, `password`, and `auth_token` options are mutually exclusive.

> [!TIP]
> You can run `which uv` to find the path to the `uv` command. This is the path you should use for the `command` field in the configuration.
>```bash
>$ which uv
>/Users/noah/.local/bin/uv
>```

You can also use environment variables to set the `username`, `password`, `auth_token`, and `endpoint` options. The environment variables are:
- `SD_USERNAME`
- `SD_PASSWORD`
- `SD_AUTH_TOKEN`
- `SD_ENDPOINT`

On Claude Desktop, you can provide an `env` object in the configuration to set these environment variables. For example:

```json
{
    "mcpServers": {
        "stardog": {
            "command": "/Users/noah/.local/bin/uv",
            "args": [
                "--directory",
        "/Users/noah/projects/mcp-server-stardog",
                "run",
                "mcp-server-stardog"
            ],
            "env": {
                "SD_USERNAME": "anonymous",
                "SD_PASSWORD": "anonymous",
                "SD_ENDPOINT": "https://express.stardog.cloud:5820"
            }
        }
    }
}
```

## Tools

### Databases
- **list_databases** - List all Stardog databases in the Stardog server.
  - No parameters required.
- **get_database_size** - Get the estimated size of a Stardog database in triples.
  - `database_name` (string, required): Name of the Stardog database.
- **get_database_configuration** - Get the configuration of a Stardog database. Optionally filter by specific keys.
  - `database_name` (string, required): Name of the Stardog database.
  - `option_keys` (string[], optional): List of specific database option keys to filter the configuration.
- **get_database_configuration_documentation** - Get documentation for Stardog database configuration options.
  - No parameters required.

### Query

- **execute_sparql_read** - Execute a SPARQL read query. `SELECT`, `CONSTRUCT`, `DESCRIBE`, and `ASK` queries are supported.
  - `query` (string, required): The SPARQL query to execute
  - `database` (string, required): The database to execute the query against.
  - `query_type` (string, optional): The query type. Acceptable values are `select`, `construct`, `describe`, and `ask`. Default is `select`.
  - `reasoning` (boolean, optional): Whether to enable reasoning when executing the query. Default is `false`.
  - `schema` (string, optional): The reasoning schema to use when executing the query. Default is `default`.
  - `limit` (int, optional): The limit for query results. Defaults to `1000`. May be useful if LLM is limited in context size.
  - `timeout_ms` (int, optional): The timeout for the query in milliseconds. Default is `30000` (30 seconds).

- **list_stored_queries** - List all stored queries in the Stardog server.
  - No parameters required.

### Monitoring

- **list_processes** - List all processes running on the Stardog server.
  - No parameters required.
- **kill_process** - Kill a specific process running on the Stardog server.
  - `id` (string, required): ID of the process to kill.
- **get_server_metrics** - Get server metrics for the Stardog server.
  - No parameters required.

### Roles
- **list_roles** - List all roles in the Stardog server. Optionally include permissions. Optionally filter results to only include a subset of roles.
  - `include_permissions` (boolean, optional): Whether to include permissions assigned to the roles.
  - `roles_filter` (string[], optional): List of role names to filter the results.
- **get_users_with_role** - List the names of users assigned to a role
  - `role_name`: (string, required): Name of the role
- **create_role** - Create a new role in the Stardog server.
  - `role_name` (string, required): Name of the role to create.
- **assign_role_to_user** - Assign a role to a specific user.
  - `role_name` (string, required): Name of the role.
  - `username` (string, required): Username of the user.
- **revoke_role_from_user** - Revoke a role from a specific user.
  - `role_name` (string, required): Name of the role.
  - `username` (string, required): Username of the user.
- **assign_permission_to_role** - Assign a permission to a specific role.
  - `role_name` (string, required): Name of the role.
  - `permission` (object, required): Permission to assign to the role. The permission object should contain the following fields:
    - `action` (string, required): The action to assign (e.g. `read`, `write`, etc.)
    - `resource_type` (string, required): The resource type (e.g. `db`, `user`, `role`, etc.)
    - `resource` (array of strings, required): The resource to assign the permission to (e.g. database name, user name, role name, *, etc.)
- **revoke_permission_from_role** - Revoke a permission from a specific role.
  - `role_name` (string, required): Name of the role.
  - `permission` (object, required): Permission to revoke from the role. The permission object should contain the following fields:
    - `action` (string, required): The action to assign (e.g. `read`, `write`, etc.)
    - `resource_type` (string, required): The resource type (e.g. `db`, `user`, `role`, etc.)
    - `resource` (array of strings, required): The resource to assign the permission to (e.g. database name, user name, role name, *, etc.)
- **delete_role** - Delete a role from the Stardog server.
  - `role_name` (string, required): Name of the role to delete.
  - `force`(boolean, optional): Forcefully delete the role (delete when still assigned to users). Default is `false`.

### Users
- **list_users** - List all users in the Stardog server. Optionally include details like permissions, superuser/active status.
  - `include_details` (boolean, optional): Whether to include detailed information about users.
  - `usernames_filter` (string[], optional): List of usernames to filter the results.
- **get_roles_assigned_to_user** - Get roles assigned to a specific user.
  - `username` (string, required): Username of the user.
- **assign_permission_to_user** - Assign a permission to a specific user.
  - `username` (string, required): Username of the user.
  - `permission` (object, required): Permission to assign to the user. The permission object should contain the following fields:
    - `action` (string, required): The action to assign (e.g. `read`, `write`, etc.)
    - `resource_type` (string, required): The resource type (e.g. `db`, `user`, `role`, etc.)
    - `resource` (array of strings, required): The resource to assign the permission to (e.g. database name, user name, role name, *, etc.)
- **revoke_permission_from_user** - Revoke a permission from a specific user.
    - `username` (string, required): Username of the user.
    - `permission` (object, required): Permission to revoke from the user. The permission object should contain the following fields:
        - `action` (string, required): The action to assign (e.g. `read`, `write`, etc.)
        - `resource_type` (string, required): The resource type (e.g. `db`, `user`, `role`, etc.)
        - `resource` (array of strings, required): The resource to assign the permission to (e.g. database name, user name, role name, *, etc.)

### Authentication
- **get_whoami** - Get information about the currently authenticated user.
  - No parameters required.

## Prompts

> [!NOTE]
> Prompts are not supported by all MCP clients yet including VS Code. Claude Desktop does support prompts.

- **database_config_helper** - Analyze the configuration of a Stardog database and generate a detailed report.
  - `database_name` (string, required): Name of the Stardog database.
  - `option_keys` (string, required): Comma-separated list of specific database option keys to filter the configuration.

- **roles_summary** - Generate a summary of roles and their permissions in the Stardog server.
  - No parameters required.
