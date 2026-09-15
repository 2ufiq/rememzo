from collections.abc import Awaitable, Callable
from typing import Annotated, Any, Literal, TypeVar
from uuid import UUID

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from rememzo import services
from rememzo.auth import RememzoTokenVerifier, get_authenticated_user_id

MemoryScope = Literal["user", "project"]
Limit = Annotated[int, Field(ge=1, le=100)]
ResultT = TypeVar("ResultT")

mcp = FastMCP(
    name="Rememzo",
    instructions="Unified MCP memory for all of your AI tools.",
    version="0.1.0",
    auth=RememzoTokenVerifier(),
)


def validate_project_scope(scope: MemoryScope, project_id: UUID | None) -> None:
    if scope == "project" and project_id is None:
        raise ToolError("project_id is required for project-scoped memory")
    if scope != "project" and project_id is not None:
        raise ToolError("project_id is only valid for project-scoped memory")


async def call_service(operation: Callable[..., Awaitable[ResultT]], *args, **kwargs) -> ResultT:
    try:
        return await operation(*args, **kwargs)
    except ValueError as error:
        raise ToolError(str(error)) from error


@mcp.tool
async def add_memory(
    content: str,
    scope: MemoryScope,
    project_id: UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """Add a memory owned by the authenticated user."""
    validate_project_scope(scope, project_id)
    return await call_service(
        services.add_memory,
        get_authenticated_user_id(),
        content,
        scope,
        project_id,
        metadata,
    )


@mcp.tool
async def fetch_memory(memory_id: UUID) -> dict:
    """Fetch one available memory by ID."""
    memory = await call_service(services.fetch_memory, get_authenticated_user_id(), memory_id)
    if memory is None:
        raise ToolError("Memory not found")
    return memory


@mcp.tool
async def search_memories(
    query: str,
    scope: MemoryScope,
    project_id: UUID | None = None,
    limit: Limit = 10,
) -> list[dict]:
    """Search memories after the separate search subsystem is installed."""
    validate_project_scope(scope, project_id)
    raise ToolError("Search is not available in this build")


@mcp.tool
async def list_memories(
    scope: MemoryScope,
    project_id: UUID | None = None,
    limit: Limit = 10,
) -> list[dict]:
    """List available memories newest first."""
    validate_project_scope(scope, project_id)
    return await call_service(
        services.list_memories,
        get_authenticated_user_id(),
        scope,
        project_id,
        limit,
    )


@mcp.tool
async def update_memory(
    memory_id: UUID,
    content: str | None = None,
    scope: MemoryScope | None = None,
    project_id: UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """Update one available owned memory."""
    memory = await call_service(
        services.update_memory,
        get_authenticated_user_id(),
        memory_id,
        content,
        scope,
        project_id,
        metadata,
    )
    if memory is None:
        raise ToolError("Memory not found")
    return memory


@mcp.tool
async def forget_memories(memory_ids: list[UUID]) -> dict:
    """Soft-delete owned memories."""
    return await call_service(services.forget_memories, get_authenticated_user_id(), memory_ids)


@mcp.tool
async def delete_memories(memory_ids: list[UUID]) -> dict:
    """Permanently delete owned memories."""
    return await call_service(services.delete_memories, get_authenticated_user_id(), memory_ids)


@mcp.tool
async def create_project(name: str, description: str | None = None) -> dict:
    """Create a project owned by the authenticated user."""
    return await call_service(
        services.create_project,
        get_authenticated_user_id(),
        name,
        description,
    )


@mcp.tool
async def fetch_project(project_id: UUID) -> dict:
    """Fetch one active owned project."""
    project = await call_service(services.fetch_project, get_authenticated_user_id(), project_id)
    if project is None:
        raise ToolError("Project not found")
    return project


@mcp.tool
async def list_projects(limit: Limit = 10) -> list[dict]:
    """List active owned projects newest first."""
    return await call_service(services.list_projects, get_authenticated_user_id(), limit)


@mcp.tool
async def update_project(
    project_id: UUID,
    name: str | None = None,
    description: str | None = None,
) -> dict:
    """Update one active owned project."""
    project = await call_service(
        services.update_project,
        get_authenticated_user_id(),
        project_id,
        name,
        description,
    )
    if project is None:
        raise ToolError("Project not found")
    return project


@mcp.tool
async def delete_project(project_id: UUID) -> dict:
    """Permanently delete one active owned project and its child rows."""
    deleted = await call_service(services.delete_project, get_authenticated_user_id(), project_id)
    if not deleted:
        raise ToolError("Project not found")
    return {"project_id": str(project_id), "deleted": True}


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)
