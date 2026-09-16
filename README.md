# Rememzo

**One shared memory for every AI client.**

Rememzo is a local-first, self-hosted MCP server that lets Codex, Claude Code, ChatGPT Desktop, and other MCP-compatible clients read and write the same persistent memories.

- Switch AI clients without losing important context
- Organize memories by user or project
- Keep your data locally in SQLite
- Protect access with user-owned API keys
- Share project memory across your team and their AI clients *(planned)*


> **Current status:** Early development. Memory and project CRUD are available.
> Search, team sharing, and one-command installation are planned. 
> Check [Rememzo Project Board](https://github.com/users/2ufiq/projects/1/views/1) for progress

## Why Rememzo?

AI clients usually keep memory inside their own local directories or product silos. Context saved in one client is unavailable when you move to another. Rememzo provides a shared MCP memory layer that you control: **AI clients change; your memory stays.**

## Quick Start

Rememzo requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run alembic upgrade head
uv run -m scripts.create_user
uv run -m scripts.create_apikey
make mcp
```

This creates the default local user, `rememzo`, and prints an API key once. Rememzo stores only the key's SHA-256 digest.

```text
API key: rmz_your_generated_key
```

The MCP endpoint is:

```text
http://127.0.0.1:8000/mcp
```

Configure your MCP client to send the API key as a bearer token:

```text
Authorization: Bearer rmz_your_generated_key
```

To create a key for another existing user, pass their username:

```bash
uv run -m scripts.create_apikey <username>
```

Rememzo v0.1 supports owner-isolated users and projects. Shared projects and role-based team access are planned for a later version.

## Available Tools

| Tool | Purpose |
| --- | --- |
| `add_memory` | Create user- or project-scoped memory |
| `fetch_memory` | Fetch one available owned memory |
| `list_memories` | List available owned memories newest first |
| `update_memory` | Update one available owned memory |
| `forget_memories` | Soft-delete owned memories |
| `delete_memories` | Permanently delete owned memories |
| `search_memories` | WIP; currently reports that search is unavailable |
| `create_project` | Create an owned project |
| `fetch_project` | Fetch one active owned project |
| `list_projects` | List active owned projects newest first |
| `update_project` | Update one active owned project |
| `delete_project` | Permanently delete a project and its child rows |

Every operation derives ownership from the bearer API key. MCP clients never submit a trusted user ID or role.

## Persistence

The default SQLite database is `rememzo.db` in the repository root. It remains on disk when the MCP server restarts and is excluded from Git. Alembic manages all database schema changes.

You can select another database location through `DATABASE_URL`. 
Use the same URL for migrations, user and API-key creation, and the running server.

## Project Structure

```text
REMEMZO
├── alembic         # Database migrations
├── docs            # Design and learning documentation
├── rememzo         # Application modules
│   ├── auth.py     # API-key authentication and identity
│   ├── db.py       # SQLAlchemy engine and session configuration
│   ├── mcp.py      # FastMCP tools and request adapters
│   ├── models.py   # Database models and constraints
│   ├── services.py # Memory and project operations
│   ├── settings.py # Shared configuration
│   └── utils.py    # Shared utilities
├── scripts         # Local management commands
└── alembic.ini     # Alembic configuration
```

## Roadmap

Development is tracked on the
[Rememzo project board](https://github.com/users/2ufiq/projects/1):

1. SQLite FTS5 memory search
2. Pytest coverage
3. Compatibility testing and guides for local AI clients
4. Cross-platform, one-command local installation

## Contributing

Rememzo is early, and this is a good time to influence how it grows. Start with an
[open issue](https://github.com/2ufiq/rememzo/issues), comment before beginning larger work,
and read the [contribution guide](CONTRIBUTING.md) for setup and pull-request expectations.

## License

Rememzo is licensed under the [Apache License 2.0](LICENSE).
