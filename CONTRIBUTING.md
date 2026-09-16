# Contributing to Rememzo

Thanks for helping build a shared, self-hosted memory layer for AI clients.
Rememzo is in early development, so small focused contributions and design feedback are both valuable.

## Find something to work on

Browse the [open issues](https://github.com/2ufiq/rememzo/issues) or the [project board](https://github.com/users/2ufiq/projects/1).
Issues labeled [`good first issue`](https://github.com/2ufiq/rememzo/labels/good%20first%20issue) are the easiest entry points.

Before starting work, leave a comment on the issue describing what you plan to do. Wait for a maintainer to approve the approach and assign the issue to you. This avoids duplicated effort and settles the scope before implementation begins.

Assignment records who is working on an issue; it does not grant repository or project-board write access. Maintainers manage the board status for external contributors:

- `Todo`: available or waiting for an agreed approach;
- `In Progress`: assigned work has started; and
- `Done`: the pull request has been merged and the issue has been closed.

## Contribution workflow

External contributors should use GitHub's
[fork-and-pull-request workflow](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project):

1. Comment on an issue with your proposed approach.
2. Wait for a maintainer to approve the scope and assign the issue.
3. Fork Rememzo and create a focused branch in your fork.
4. Make and verify the change, then push the branch to your fork.
5. Open a pull request against `2ufiq/rememzo:main`. Use `Closes #<issue-number>` in the description so GitHub closes the issue after the pull request is merged.
6. Address review feedback by pushing more commits to the same branch; the pull request updates automatically.

Open a draft pull request if you want early feedback. Mark it ready for review when the change is complete. 

## Local setup

Rememzo requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/<your-username>/rememzo.git
cd rememzo
git remote add upstream https://github.com/2ufiq/rememzo.git
git switch -c <focused-branch-name>
uv sync --locked
uv run alembic upgrade head
uv run -m scripts.create_user
uv run -m scripts.create_apikey
make mcp
```

The server starts at `http://127.0.0.1:8000/mcp`.
The generated API key is shown once.

## Project boundaries

- Keep MCP request adapters thin in `rememzo/mcp.py`.
- Put database operations and business rules in `rememzo/services.py`.
- Keep authentication and API-key identity in `rememzo/auth.py`.
- Derive the user from the bearer API key. Never trust a client-provided user ID or role.
- Make schema changes through Alembic migrations; do not create tables at application startup.
- Keep memory search separate from CRUD so its storage and ranking can evolve independently.

The design notes in [`docs/system-design.md`](docs/system-design.md) explain the current model and planned boundaries.

## Make a change

Prefer small pull requests of roughly 100 changed lines or fewer, excluding generated files. If the work is substantially larger, propose several focused sub-issues first. Submit them as separate pull requests in dependency order, and wait for the preceding change to be reviewed before starting dependent work.

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

The automated test suite is a tracked roadmap item and is not committed yet. Until it lands, describe the manual checks you performed in the pull request.

## Pull requests

A useful pull request includes:

- a short explanation of the problem and solution;
- a linked issue, when one exists;
- the checks or MCP clients used to verify the change;
- migration notes for database changes;
- no API keys, database files, or other secrets.

Maintainers may ask for a smaller scope or a design discussion before merging.
That is especially likely for authentication, ownership, team access, search ranking, and installer behavior.
