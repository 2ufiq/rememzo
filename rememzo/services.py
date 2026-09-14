# application logic here.
# mcp.py only communicate with client. the CRUD operation with db happens here.


import hashlib
from datetime import UTC
from uuid import UUID

from sqlalchemy import select

from rememzo.db import SessionFactory
from rememzo.models import APIKey, Memory
from rememzo.utils import utc_now


async def is_apikey_valid(presented_key: str):
    presented_hash = hashlib.sha256(presented_key.encode()).hexdigest()
    async with SessionFactory() as session:
        api_key = await session.scalar(
            select(APIKey).where(APIKey.key_hash == presented_hash)
        )
        if not api_key or not api_key.is_active:
            return False
        if api_key.expired_at:
            expired_at = api_key.expired_at
            if expired_at.tzinfo is None:
                expired_at = expired_at.replace(tzinfo=UTC)
            if expired_at <= utc_now():
                return False
        return True


async def get_user_id_from_apikey(presented_key: str) -> UUID | None:
    presented_hash = hashlib.sha256(presented_key.encode()).hexdigest()
    async with SessionFactory() as session:
        return await session.scalar(
            select(APIKey.user_id).where(APIKey.key_hash == presented_hash)
        )


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
