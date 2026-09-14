import os

APIKEY_PREFIX = os.environ.get("APIKEY_PREFIX", "rmz_")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./rememzo.db")

# Default User's credentials
username = os.environ.get("username", "rememzo")
name = os.environ.get("name", "rememzo")
email = os.environ.get("email", "rememzo@rememzo.com")
password = os.environ.get("password", "secret")