import argparse
import asyncio
import hashlib
import logging
import secrets
import sys

from sqlalchemy import select

from rememzo import settings
from rememzo.db import SessionFactory
from rememzo.models import APIKey, User


# TODO: extend to management cmd
async def create_apikey(username: str = settings.username) -> str | None:
    async with SessionFactory() as session:
        user = await session.scalar(
            select(User).where(User.username == username)
        )
        if user is None:
            logging.warning("No user with username=%s", username)
            return

        logging.info(
            "Creating API key for: user_id=%s username=%s",
            user.id,
            user.username,
        )
        raw_key = settings.APIKEY_PREFIX + secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        api_key = APIKey(
            user_id=user.id,
            key_hash=key_hash,
        )
        session.add(api_key)
        await session.commit()
        # sys.stdout.write(f"\nCreated APIKey: {raw_key} for username: {user.username}\n")
        return raw_key


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a Rememzo API key")
    parser.add_argument(
        "username",
        nargs="?",
        default=settings.username,
        help=f"Key owner (default: {settings.username})",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    created_key = asyncio.run(create_apikey(args.username))
    if created_key is None:
        raise SystemExit(1)

    print(f"API key: {created_key}")
