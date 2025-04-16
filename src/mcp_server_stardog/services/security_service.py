from __future__ import annotations
from typing import TYPE_CHECKING, Literal
import logging

from pydantic import BaseModel, Field


if TYPE_CHECKING:
    from ..stardog_client import StardogClient

logger = logging.getLogger("mcp_server_stardog")


class Permission(BaseModel):
    """
    Represents a permission in Stardog.
    """

    action: Literal[
        "read", "write", "create", "delete", "revoke", "grant", "execute", "all"
    ] = Field(description="The action to be performed. `all ` means all actions.")
    resource_type: Literal[
        "db",
        "metadata",
        "user",
        "role",
        "named-graph",
        "virtual-graph",
        "data-source",
        "dbms-admin",
        "admin",
        "sensitive-property",
        "stored-query",
        "*",
    ] = Field(description="The type of resource. `*` means all resource types.")
    resource: list[str] = Field(
        description="The specific resource(s) to which the permission applies. In most cases, a single resource (list of 1 string) is expected. The * character is used to indicate all resources of the specified type."
    )


class SecurityService:
    """
    Handles security related operations in Stardog.
    """

    def __init__(self, client: StardogClient):
        self.client = client

    async def list_roles(self) -> list[str]:
        """
        Get the list of roles from Stardog.
        """
        url = f"{self.client.endpoint}/admin/roles"
        response = await self.client._get(url, None)
        data = response.json()
        return data.get("roles", [])

    async def list_roles_with_permissions(self) -> list[dict]:
        """
        Get the list of roles with their permissions from Stardog.
        """
        url = f"{self.client.endpoint}/admin/roles/list"
        response = await self.client._get(url, None)
        return response.json()

    async def get_role_permissions(self, role_name: str) -> dict:
        """
        Get the permissions for a specific role in Stardog.
        """
        url = f"{self.client.endpoint}/admin/permissions/role/{role_name}"
        response = await self.client._get(url, None)
        data = response.json()
        return data.get("permissions", [])

    async def get_users_with_role(self, role_name: str) -> list[str]:
        """
        Get the users associated with a specific role in Stardog.
        """
        url = f"{self.client.endpoint}/admin/roles/{role_name}/users"
        response = await self.client._get(url, None)
        data = response.json()
        return data.get("users", [])

    async def get_whoami(self) -> dict:
        """
        Get the username of the current authenticated user from Stardog.
        """
        url = f"{self.client.endpoint}/admin/status/whoami"
        response = await self.client._get(url, None)
        return response.text

    async def get_roles_assigned_to_user(self, username: str) -> list[str]:
        """
        Get the roles assigned to a specific user in Stardog.
        """
        url = f"{self.client.endpoint}/admin/users/{username}/roles"
        response = await self.client._get(url, None)
        data = response.json()
        return data.get("roles", [])

    async def get_user_with_details(self, username: str) -> dict:
        """
        Get the details of a specific user in Stardog. Details include:
            - roles
            - permissions
            - enabled/disabled status
            - superuser status
        """
        url = f"{self.client.endpoint}/admin/users/{username}"
        response = await self.client._get(url, None)
        return response.json()

    async def get_users_with_details(self) -> list[dict] | None:
        """
        Get all users with their:
            - roles
            - permissions
            - enabled/disabled status
            - superuser status
        """
        url = f"{self.client.endpoint}/admin/users/list"
        response = await self.client._get(url, None)
        if response:
            return response.json()
        return None

    async def list_users(self) -> list[str]:
        """
        Get the list of users (without details) from Stardog.
        """
        url = f"{self.client.endpoint}/admin/users"
        response = await self.client._get(url, None)
        data = response.json()
        return data.get("users", [])

    async def create_role(self, role_name: str) -> None:
        """
        Create a new role in Stardog.
        """
        url = f"{self.client.endpoint}/admin/roles"
        data = {"rolename": role_name}
        await self.client._post(url, None, json=data)
        return None

    async def delete_role(self, role_name: str, force: bool = False) -> None:
        """
        Delete a role in Stardog.
        """
        url = f"{self.client.endpoint}/admin/roles/{role_name}"
        await self.client._delete(url, None, params={"force": force})
        return None

    async def assign_role_to_user(self, role_name: str, username: str) -> None:
        """
        Assign a role to a user in Stardog.
        """
        url = f"{self.client.endpoint}/admin/users/{username}/roles"
        data = {"rolename": role_name}
        await self.client._post(url, None, json=data)
        return None

    async def revoke_role_from_user(self, role_name: str, username: str) -> None:
        """
        Revoke a role from a user in Stardog.
        """
        url = f"{self.client.endpoint}/admin/users/{username}/roles/{role_name}"
        await self.client._delete(url, None)
        return None

    async def assign_permission_to_role(
        self, role_name: str, permission: Permission
    ) -> None:
        """
        Assign permission to a role in Stardog.
        """
        url = f"{self.client.endpoint}/admin/permissions/role/{role_name}"
        await self.client._put(url, None, json=permission.model_dump())
        return None

    async def revoke_permission_from_role(
        self, role_name: str, permission: Permission
    ) -> None:
        """
        Revoke permission from a role in Stardog.
        """
        url = f"{self.client.endpoint}/admin/permissions/role/{role_name}/delete"
        await self.client._post(url, None, json=permission.model_dump())
        return None

    async def assign_permission_to_user(
        self, username: str, permission: Permission
    ) -> None:
        """
        Assign permission to a user in Stardog.
        """
        url = f"{self.client.endpoint}/admin/permissions/user/{username}"
        await self.client._put(url, None, json=permission.model_dump())
        return None

    async def revoke_permission_from_user(
        self, username: str, permission: Permission
    ) -> None:
        """
        Revoke permission from a user in Stardog.
        """
        url = f"{self.client.endpoint}/admin/permissions/user/{username}/delete"
        await self.client._post(url, None, json=permission.model_dump())
        return None
