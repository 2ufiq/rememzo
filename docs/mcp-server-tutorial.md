After public release or deployment, we will publish a tutorial on "How to build an MCP server". 
We build the tutorial steps and concepts on this doc based on the rememzo building process.

Tutorial title:
- How to build an MCP server? Learn only whats needed.
- How to build an MCP server step-by-step.

## Draft table of content

### Concept
1. Differences among MCP servers, clients, and Apps
2. Core components: Tools, resource, prompts
3. Understand and diagram design for Rememzo: Idea, requirements, top level system diagram.
4. Discuss each composents and tech stack: DB (sqlite, sqlalchemy), MCP server (FastMCP), Auth (APIkey), MCP Client (Claude eco, ChatGPT echo)

### Implementation
1. venv setup via uv, fastmcp install
   - https://docs.astral.sh/uv/getting-started/installation/
   - https://gofastmcp.com/getting-started/installation
2. Write simple MCP tools and run server (stdio and http, when to use what)
   - https://gofastmcp.com/getting-started/quickstart
3. Use local MCP server via ClaudeDesktop, ClaudeCode. No Auth, No DB.
4. Expose local MCP server via tunnel and use via Claude.ai and ChatGPT. Read/Write a local json file as memory store.
5. Install async SQLAlchemy, write ORM, add SQLite DB and Alembic for migration. Lastly read/write db by MCP client via MCP tools.
   - https://docs.sqlalchemy.org/en/21/orm/extensions/asyncio.html
   - https://docs.sqlalchemy.org/en/21/orm/quickstart.html
   - https://pypi.org/project/aiosqlite/
   - https://docs.sqlalchemy.org/en/21/dialects/sqlite.html#transactions-with-sqlite-and-the-sqlite3-driver
6. Add APIkey auth (User and Auth Model, application logic) and reconnect to MCP server
   - https://gofastmcp.com/servers/auth/authentication


TBA:
- Capacity read/write per second.


### Audience Level:
1. Required: Python
2. Good to have: understanding of databases, python based projects

