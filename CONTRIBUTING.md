# Contributing to Rememzo

Thanks for helping build a shared, self-hosted memory layer for AI clients.
Rememzo is in early development, so small focused contributions and design feedback are both
valuable.

## Find something to work on

Browse the [open issues](https://github.com/2ufiq/rememzo/issues) or the
[project board](https://github.com/users/2ufiq/projects/1). Issues labeled
[`good first issue`](https://github.com/2ufiq/rememzo/labels/good%20first%20issue) are the easiest
entry points.

Before starting substantial work, leave a comment on the issue describing what you plan to do.
This helps avoid duplicated effort and gives us a chance to settle the approach first.

## Local setup

Rememzo requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/2ufiq/rememzo.git
cd rememzo
uv sync --locked
uv run alembic upgrade head
uv run -m scripts.create_user
uv run -m scripts.create_apikey
make mcp
```

The server starts at `http://127.0.0.1:8000/mcp`. The generated API key is shown once; do not
commit it, paste it into an issue, or include it in logs.

## Project boundaries

- Keep MCP request adapters thin in `rememzo/mcp.py`.
- Put database operations and business rules in `rememzo/services.py`.
- Keep authentication and API-key identity in `rememzo/auth.py`.
- Derive the user from the bearer API key. Never trust a client-provided user ID or role.
- Make schema changes through Alembic migrations; do not create tables at application startup.
- Keep memory search separate from CRUD so its storage and ranking can evolve independently.

The design notes in [`docs/system-design.md`](docs/system-design.md) explain the current model and
planned boundaries.

## Make a change

1. Create a focused branch from `main`.
2. Keep the change limited to one issue or concern.
3. Add or update documentation when behavior or setup changes.
4. Run the available checks:

   ```bash
   uv run ruff format --check .
   uv run ruff check .
   uv run alembic upgrade head
   ```

5. Open a pull request and link the issue it addresses.

The automated test suite is a tracked roadmap item and is not committed yet. Until it lands,
describe the manual checks you performed in the pull request.

## Pull requests

A useful pull request includes:

- a short explanation of the problem and solution;
- a linked issue, when one exists;
- the checks or MCP clients used to verify the change;
- migration notes for database changes; and
- no API keys, database files, or other secrets.

Maintainers may ask for a smaller scope or a design discussion before merging. That is especially
likely for authentication, ownership, team access, search ranking, and installer behavior.
