# Rememzo

An unified MCP-server based memory for all of the local AI agents.


## Quick Start

Rememzo requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

### Local Setup
```bash
uv sync
uv run alembic upgrade head
uv run -m scripts.create_user
uv run -m scripts.create_apikey
make mcp
```

It will create an default user `rememzo` and print an APIKey `rmz...`. For single use, the default user is fine. For team project, use `scripts.create_user` to create new user.

```sh
# Default User
username: rememzo
password: sectet
email: rememzo@rememzo.com

# Example APIKey
rmz_HF9YryObegrawJDOguFpgaD6umawcrl1nM1n7GTV6XU
```

You have to use the APIKey to connect **Rememzo** with your MCP-clients (eg. Codex, Claude-Code, Claude Desktop, ChatGPT Desktop). 

To create a key for another existing user, pass the username:

```bash
uv run -m scripts.create_apikey <username>
```

### Run MCP Server
Start the MCP HTTP server:

```bash
make mcp
```

The MCP endpoint is `http://127.0.0.1:8000/mcp`. 


## Tools

| Tool | Purpose |
| --- | --- |
| `add_memory` | Create user or project-scoped memory |
| `fetch_memory` | Fetch one available owned memory |
| `list_memories` | List available owned memories newest first |
| `update_memory` | Update one available owned memory |
| `forget_memories` | Soft-delete owned memories |
| `delete_memories` | Permanently delete owned memories |
| `search_memories` | FTS5 search workstream |
| `create_project` | Create an owned project |
| `fetch_project` | Fetch one active owned project |
| `list_projects` | List active owned projects newest first |
| `update_project` | Update one active owned project |
| `delete_project` | Permanently delete a project and its child rows |
