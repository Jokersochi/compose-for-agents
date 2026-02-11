# AGENTS.md

Guidance for automated coding agents working in this repository.

## Scope

- These instructions apply to the whole repository unless a deeper `AGENTS.md` exists.
- This repository is a monorepo of mostly independent demo projects.

## Repository layout

- `README.md`: top-level prerequisites and demo catalog.
- `<demo>/README.md`: source of truth for each demo's setup and behavior.
- `.github/workflows/`: CI definitions (markdown, yaml, and demo workflows).
- `Taskfile.yaml`: root lint helper tasks.

## Working model

1. Identify the single demo directory that the task affects.
2. Read that demo's `README.md` and compose files before editing.
3. Keep changes scoped to the requested demo unless cross-demo updates are required.
4. Avoid adding runtime dependencies unless the task requires them.

## Setup and run

- Run demos from the demo directory with `docker compose up --build`.
- Demos that support OpenAI mode can usually be run with:
  1. a `secret.openai-api-key` file containing the key
  2. `docker compose -f compose.yaml -f compose.openai.yaml up`

## Validation

Run only checks relevant to touched files.

### Repository-wide checks

- `task lint:markdown`
- `task lint:yaml`
- `task lint`

### Language-specific checks

- Python demos: use project-configured tools (commonly `ruff check` and `ruff format`).
- Go demo (`langchaingo`): `go test ./...`.
- Java demo (`spring-ai`): `./mvnw test` when Java sources change.

## Compose and secrets guidelines

- Never commit real credentials or secrets.
- Use sample files such as `.env.sample` and `.mcp.env.example` as templates.
- Prefer local `.mcp.env` files for MCP secrets referenced by compose `secrets`.
- Keep model definitions and service model mappings consistent after model changes.

## Documentation expectations

- Update the relevant demo `README.md` when setup or behavior changes.
- Keep markdown readable and lint-friendly (the repo uses markdownlint with 120-char lines).
- Prefer concise examples that can be copied and run directly.

## Commit guidance

- Make focused commits with descriptive commit messages.
- Include brief rationale in commit bodies when changes are not obvious.
