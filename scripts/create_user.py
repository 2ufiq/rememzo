import logging
import asyncio

from sqlalchemy import select

from rememzo.db import SessionFactory
from rememzo.models import User
from rememzo import settings

# TODO: extend to management cmd
async def create_default_user():
    async with SessionFactory() as session:
        
        user = await session.scalar(
            select(User).where(User.username==settings.username)
        )
        if user is not None:
            logging.info(
                "User already exists: id=%s username=%s email=%s name=%s",
                user.id,
                user.username,
                user.email,
                user.name,
            )
            return user
        
        user = User(
            username=settings.username,
            name=settings.name,
            email=settings.email,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logging.info(
            "User created: id=%s username=%s email=%s name=%s",
            user.id,
            user.username,
            user.email,
            user.name,
        )
        return user
        
if __name__=="__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    asyncio.run(create_default_user())
