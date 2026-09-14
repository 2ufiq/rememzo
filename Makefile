mcp:
	uv run -m rememzo.mcp

ruff:
	uv run ruff format
	uv run ruff check --fix