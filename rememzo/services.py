# application logic here.
# mcp.py only communicate with client. the CRUD operation with db happens here.


import hashlib
from datetime import UTC
from uuid import UUID

from sqlalchemy import select

from rememzo.db import SessionFactory
from rememzo.models import APIKey, Memory
from rememzo.utils import utc_now



def serialize_memory(memory: Memory) -> dict:
    return {
        "memory_id": str(memory.id),
        "content": memory.content,
        "scope": memory.scope,
        "project_id": (str(memory.project_id) if memory.project_id is not None else None),
        "extra": memory.extra,
        "created_at": memory.created_at.isoformat(),
        "updated_at": memory.updated_at.isoformat(),
    }


async def add_memory(
    user_id: UUID,
    content: str,
    scope: str = "user",
    project_id: UUID | None = None,
    extra: dict | None = None,
) -> dict:
    async with SessionFactory() as session:
        memory = Memory(
            user_id=user_id,
            project_id=project_id,
            content=content,
            scope=scope,
            extra=extra or {},
        )
        session.add(memory)
        await session.commit()
        await session.refresh(memory)
        return serialize_memory(memory)


async def fetch_memory(memory_id: UUID) -> dict | None:
    async with SessionFactory() as session:
        memory = await session.get(Memory, memory_id)
        if memory is None or not memory.is_active:
            return None
        return serialize_memory(memory)
