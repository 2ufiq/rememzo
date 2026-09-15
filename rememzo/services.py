from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from rememzo.db import SessionFactory
from rememzo.models import Memory, Project
from rememzo.utils import utc_now


def serialize_memory(memory: Memory) -> dict:
    return {
        "memory_id": str(memory.id),
        "content": memory.content,
        "scope": memory.scope,
        "project_id": str(memory.project_id) if memory.project_id is not None else None,
        "extra": memory.extra,
        "created_at": memory.created_at.isoformat(),
        "updated_at": memory.updated_at.isoformat(),
    }


def validate_limit(limit: int) -> None:
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")


def validate_content(content: str) -> None:
    if not content.strip():
        raise ValueError("content must contain non-whitespace text")


def validate_scope(scope: str, project_id: UUID | None) -> None:
    if scope == "project" and project_id is None:
        raise ValueError("project_id is required for project-scoped memory")
    if scope == "user" and project_id is not None:
        raise ValueError("project_id is only valid for project-scoped memory")
    if scope not in {"user", "project"}:
        raise ValueError("scope must be 'user' or 'project'")


def available_memory_conditions(user_id: UUID) -> tuple:
    return (
        Memory.user_id == user_id,
        Memory.is_active.is_(True),
        or_(Memory.expired_at.is_(None), Memory.expired_at > utc_now()),
    )


async def require_owned_active_project(
    session: AsyncSession,
    user_id: UUID,
    project_id: UUID,
) -> Project:
    project = await session.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == user_id,
            Project.is_active.is_(True),
        )
    )
    if project is None:
        raise ValueError("project_id must identify an active owned project")
    return project


def unique_ids(memory_ids: Iterable[UUID]) -> list[UUID]:
    return list(dict.fromkeys(memory_ids))


async def add_memory(
    user_id: UUID,
    content: str,
    scope: str = "user",
    project_id: UUID | None = None,
    extra: dict | None = None,
) -> dict:
    validate_content(content)
    validate_scope(scope, project_id)

    async with SessionFactory() as session:
        if project_id is not None:
            await require_owned_active_project(session, user_id, project_id)

        memory = Memory(
            user_id=user_id,
            project_id=project_id,
            content=content,
            scope=scope,
            extra=extra if extra is not None else {},
        )
        session.add(memory)
        await session.commit()
        await session.refresh(memory)
        return serialize_memory(memory)


async def fetch_memory(user_id: UUID, memory_id: UUID) -> dict | None:
    async with SessionFactory() as session:
        memory = await session.scalar(
            select(Memory).where(
                Memory.id == memory_id,
                *available_memory_conditions(user_id),
            )
        )
        return serialize_memory(memory) if memory is not None else None


async def list_memories(
    user_id: UUID,
    scope: str,
    project_id: UUID | None = None,
    limit: int = 10,
) -> list[dict]:
    validate_limit(limit)
    validate_scope(scope, project_id)

    async with SessionFactory() as session:
        if project_id is not None:
            await require_owned_active_project(session, user_id, project_id)

        memories = await session.scalars(
            select(Memory)
            .where(
                *available_memory_conditions(user_id),
                Memory.scope == scope,
                Memory.project_id == project_id,
            )
            .order_by(Memory.created_at.desc(), Memory.id.asc())
            .limit(limit)
        )
        return [serialize_memory(memory) for memory in memories]


async def update_memory(
    user_id: UUID,
    memory_id: UUID,
    content: str | None = None,
    scope: str | None = None,
    project_id: UUID | None = None,
    extra: dict | None = None,
) -> dict | None:
    if all(value is None for value in (content, scope, project_id, extra)):
        raise ValueError("At least one field must be provided for update")
    if content is not None:
        validate_content(content)
    if scope is None and project_id is not None:
        raise ValueError("project_id requires scope='project' to be set explicitly")
    if scope is not None:
        validate_scope(scope, project_id)

    async with SessionFactory() as session:
        memory = await session.scalar(
            select(Memory).where(
                Memory.id == memory_id,
                *available_memory_conditions(user_id),
            )
        )
        if memory is None:
            return None

        if scope == "project":
            await require_owned_active_project(session, user_id, project_id)

        if content is not None:
            memory.content = content
        if scope is not None:
            memory.scope = scope
            memory.project_id = project_id if scope == "project" else None
        if extra is not None:
            memory.extra = extra

        await session.commit()
        await session.refresh(memory)
        return serialize_memory(memory)


async def forget_memories(user_id: UUID, memory_ids: Iterable[UUID]) -> dict:
    requested_ids = unique_ids(memory_ids)
    if not requested_ids:
        return {"requested_count": 0, "affected_count": 0, "affected_ids": []}

    async with SessionFactory() as session:
        existing_ids = set(
            await session.scalars(
                select(Memory.id).where(
                    Memory.id.in_(requested_ids),
                    *available_memory_conditions(user_id),
                )
            )
        )
        affected_ids = [memory_id for memory_id in requested_ids if memory_id in existing_ids]
        if affected_ids:
            await session.execute(
                update(Memory)
                .where(Memory.id.in_(affected_ids), Memory.user_id == user_id)
                .values(is_active=False)
            )
            await session.commit()

    return {
        "requested_count": len(requested_ids),
        "affected_count": len(affected_ids),
        "affected_ids": [str(memory_id) for memory_id in affected_ids],
    }


async def delete_memories(user_id: UUID, memory_ids: Iterable[UUID]) -> dict:
    requested_ids = unique_ids(memory_ids)
    if not requested_ids:
        return {"requested_count": 0, "affected_count": 0, "affected_ids": []}

    async with SessionFactory() as session:
        existing_ids = set(
            await session.scalars(
                select(Memory.id).where(
                    Memory.id.in_(requested_ids),
                    Memory.user_id == user_id,
                )
            )
        )
        affected_ids = [memory_id for memory_id in requested_ids if memory_id in existing_ids]
        if affected_ids:
            await session.execute(
                delete(Memory).where(
                    Memory.id.in_(affected_ids),
                    Memory.user_id == user_id,
                )
            )
            await session.commit()

    return {
        "requested_count": len(requested_ids),
        "affected_count": len(affected_ids),
        "affected_ids": [str(memory_id) for memory_id in affected_ids],
    }


def serialize_project(project: Project) -> dict:
    return {
        "project_id": str(project.id),
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
    }


def validate_project_name(name: str) -> None:
    if not name.strip():
        raise ValueError("name must contain non-whitespace text")


async def create_project(
    user_id: UUID,
    name: str,
    description: str | None = None,
) -> dict:
    validate_project_name(name)
    async with SessionFactory() as session:
        project = Project(
            user_id=user_id,
            name=name,
            description=description or None,
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return serialize_project(project)


async def fetch_project(user_id: UUID, project_id: UUID) -> dict | None:
    async with SessionFactory() as session:
        project = await session.scalar(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == user_id,
                Project.is_active.is_(True),
            )
        )
        return serialize_project(project) if project is not None else None


async def list_projects(user_id: UUID, limit: int = 10) -> list[dict]:
    validate_limit(limit)
    async with SessionFactory() as session:
        projects = await session.scalars(
            select(Project)
            .where(
                Project.user_id == user_id,
                Project.is_active.is_(True),
            )
            .order_by(Project.created_at.desc(), Project.id.asc())
            .limit(limit)
        )
        return [serialize_project(project) for project in projects]


async def update_project(
    user_id: UUID,
    project_id: UUID,
    name: str | None = None,
    description: str | None = None,
) -> dict | None:
    if name is None and description is None:
        raise ValueError("At least one field must be provided for update")
    if name is not None:
        validate_project_name(name)

    async with SessionFactory() as session:
        project = await session.scalar(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == user_id,
                Project.is_active.is_(True),
            )
        )
        if project is None:
            return None

        if name is not None:
            project.name = name
        if description is not None:
            project.description = description or None

        await session.commit()
        await session.refresh(project)
        return serialize_project(project)


async def delete_project(user_id: UUID, project_id: UUID) -> bool:
    async with SessionFactory() as session:
        result = await session.execute(
            delete(Project).where(
                Project.id == project_id,
                Project.user_id == user_id,
                Project.is_active.is_(True),
            )
        )
        if result.rowcount == 0:
            return False
        await session.commit()
        return True
