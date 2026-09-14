from typing import Any, Literal
from uuid import UUID

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError

from rememzo import services
from rememzo.auth import RememzoTokenVerifier, get_authenticated_user_id

MemoryScope = Literal["user", "project"]


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


@mcp.tool
async def add_memory(
    content: str,
    scope: MemoryScope,
    project_id: UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """Add memory"""
    validate_project_scope(scope, project_id)
    return await services.add_memory(
        user_id=get_authenticated_user_id(),
        content=content,
        scope=scope,
        project_id=project_id,
        extra=metadata,
    )


@mcp.tool
async def fetch_memory(memory_id: UUID) -> dict:
    """Fetch one specific memory by ID"""
    return await services.fetch_memory(memory_id)


@mcp.tool
async def search_memories(
    query: str,
    scope: MemoryScope,
    project_id: UUID | None = None,
    limit: int = 10,
) -> list[dict]:
    """Search N last memories"""
    validate_project_scope(scope, project_id)
    memories = [
        {
            "content": "sample memory",
            "memory_id": "sample memory id",
        }
    ]
    return memories


@mcp.tool
async def list_memories(
    scope: MemoryScope,
    project_id: UUID | None = None,
    limit: int = 10,
) -> list[dict]:
    """List N last memories"""
    validate_project_scope(scope, project_id)
    memories = [
        {
            "content": "sample memory",
            "memory_id": "sample memory id",
        }
    ]
    return memories


@mcp.tool
async def update_memory(
    memory_id: UUID,
    content: str | None = None,
    scope: MemoryScope | None = None,
    project_id: UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Update existing memory"""
    if all(value is None for value in (content, scope, project_id, metadata)):
        raise ToolError("At least one field must be provided for update")

    if scope is not None:
        validate_project_scope(scope, project_id)

    return f"updated memory {memory_id}"


@mcp.tool
async def forget_memories(memory_ids: list[UUID]) -> str:
    """Forget one specific existing memory"""
    return f"forgot memories {memory_ids}"


@mcp.tool
async def delete_memories(memory_ids: list[UUID], ctx: Context) -> str:
    """Delete existing memories"""
    await ctx.info(f"deleting memories {memory_ids}")
    return f"deleted memories {memory_ids}"


# TODO:
# create/retrieve/update/delete project
# list projects
#


@mcp.resource("data://config")
def get_config() -> dict:
    return {"theme": "dark", "version": "1.0"}


@mcp.prompt
def analyze_datapoints(datapoints: list) -> str:
    datapoints = sorted(datapoints)
    return f"Please analyze these datapoints: {datapoints}"


if __name__ == "__main__":
    # run as stdio
    # mcp.run()

    # add to claude desktop ` ~/.config/Claude/claude_desktop_config.json`
    # {
    # "mcpServers": {
    #     "rememzo": {
    #     "command": "uv",
    #     "args": ["run", "--directory", "<path-to-rememzo>", "main.py"]
    #     }
    # }
    # }

    # run http
    mcp.run(transport="http", host="127.0.0.1", port=8000)
    #
    # add to claude desktop ` ~/.config/Claude/claude_desktop_config.json`
    # {
    # "mcpServers": {
    #     "rememzo": {
    #     "url": "http://localhost:PORT/mcp"
    #     }
    # }
    # }
