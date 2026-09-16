import sqlite3
from unittest.mock import MagicMock

from conftest import load_plugin_module
from fake_plugin_context import FakePluginContext


class _DbModule:
    def __init__(self, conn):
        self._conn = conn

    def get_db(self):
        return self._conn


def _make_plugin(tmp_path, conn):
    vault = MagicMock()
    vault.vault_path = lambda name: tmp_path / "vault"
    vault.extract_frontmatter_field = lambda content, field: None
    ctx = FakePluginContext(vault_manager=vault, db_module=_DbModule(conn))
    plugin = load_plugin_module().Plugin()
    plugin.on_load(ctx)
    return plugin


def test_digest_survives_missing_chat_table(tmp_path):
    (tmp_path / "vault").mkdir()
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    plugin = _make_plugin(tmp_path, conn)
    result = plugin._build_digest("main")
    assert result["conversation_count"] == 0


def test_digest_counts_chat_threads_when_present(tmp_path):
    (tmp_path / "vault").mkdir()
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE chat_threads (id INTEGER PRIMARY KEY, vault_name TEXT)")
    conn.execute("INSERT INTO chat_threads (vault_name) VALUES ('main')")
    conn.execute("INSERT INTO chat_threads (vault_name) VALUES ('other')")
    plugin = _make_plugin(tmp_path, conn)
    result = plugin._build_digest("main")
    assert result["conversation_count"] == 1
