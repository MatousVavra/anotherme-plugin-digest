# anotherme-plugin-digest

Snapshot of projects, people, mood, and pending questions for
[AnotherMe](https://github.com/MatousVavra/AnotherMe).

Extracted from the AnotherMe host repository at commit 9a6ef26 — prior
history lives there.

## Configuration

| Env var | Default | Purpose |
|---|---|---|
| `AI_BASE_URL` | `https://llm.ai.e-infra.cz/v1/` | AI provider base URL (used by the host LLM client via `ctx.llm_client`) |
| `AI_API_KEY` | — | AI provider API key |

The digest is computed on demand every time the Digest tab loads or its
Refresh button is pressed. When a diary entry is saved, the plugin records
a `digest_data_updated_at` timestamp in its store; every rendered digest
records `digest_refreshed_at`.

## Development

Unit tests run standalone against `FakePluginContext`:

    pip install fastapi pydantic httpx pyyaml pytest pytest-asyncio openai
    pytest tests/ --ignore=tests/integration

Integration tests run inside the released app image (see
`.github/workflows/test.yml`). To develop against a live app, point
`COMMUNITY_PLUGINS_DIR` at this checkout's parent directory.

## Releases

Tag `vX.Y.Z` (must match `plugin/plugin.yaml` `version`), then bump the tag
in the [community index](https://github.com/MatousVavra/anotherme-plugins).
