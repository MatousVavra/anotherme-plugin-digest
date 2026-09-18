import sqlite3
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from conftest import load_plugin_module
from fake_plugin_context import FakePluginContext


class _DbModule:
    def __init__(self, conn):
        self._conn = conn

    def get_db(self):
        return self._conn


def _make_loaded_plugin(tmp_path):
    vault = MagicMock()
    vault.vault_path = lambda name: tmp_path / "vault"
    vault.extract_frontmatter_field = lambda content, field: None
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    ctx = FakePluginContext(vault_manager=vault, db_module=_DbModule(conn))
    ctx.plugin_name = "digest"
    plugin = load_plugin_module().Plugin()
    plugin.on_load(ctx)
    return ctx


def _client_for(ctx):
    app = FastAPI()
    for name, router in ctx.registry.routers:
        app.include_router(router, prefix=f"/plugins/{name}")
    return TestClient(app)


def test_diary_saved_records_data_updated_timestamp(tmp_path):
    import asyncio

    ctx = _make_loaded_plugin(tmp_path)
    asyncio.run(ctx.event_bus.emit("diary_saved", {"content": "hello", "mood": "ok"}))
    assert ctx.store.get("digest_data_updated_at")


def test_digest_route_records_refreshed_timestamp(tmp_path):
    (tmp_path / "vault").mkdir(parents=True, exist_ok=True)
    ctx = _make_loaded_plugin(tmp_path)
    with _client_for(ctx) as client:
        resp = client.get("/plugins/digest")
        assert resp.status_code == 200
        assert ctx.store.get("digest_refreshed_at")
