"""Digest plugin integration tests (moved from the AnotherMe host repo,
tests/test_plugins/test_remaining_plugins.py)."""
import os
from pathlib import Path
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client(make_client):
    return make_client()


class FakeMemoryApi:
    def __init__(self, people=None, facts=None):
        self._people = people or []
        self._facts = facts or []

    def get_people(self, vault_name):
        return self._people

    def get_facts(self, vault_name):
        return self._facts


def _seed_digest_data(vault_dir):
    """Create a project and a diary entry with mood in the vault."""
    proj_dir = vault_dir / "Projects"
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / "MyProject.md").write_text(
        "---\ntitle: My Project\nstatus: active\n---\n\n# My Project\n\nWork in progress.\n",
        encoding="utf-8",
    )

    diary_dir = vault_dir / "Diary"
    diary_dir.mkdir(parents=True, exist_ok=True)
    (diary_dir / "Diary-2026-08-21.md").write_text(
        "---\nmood: cheerful\ndate: 2026-08-21\n---\n\n# Today\n\nGood day.\n",
        encoding="utf-8",
    )


# ===========================================================================
# Digest plugin
# ===========================================================================

def test_digest_plugin_listed(client):
    names = {p["name"] for p in client.get("/plugins").json()}
    assert "digest" in names


def test_digest_returns_correct_shape(client):
    vault_dir = Path(os.environ["VAULTS_DIR"]) / "test-main"
    _seed_digest_data(vault_dir)

    fake_api = FakeMemoryApi(
        people=[{"name": "Alice"}],
        facts=[{"key": "name", "value": "Bob"}],
    )

    import src.main
    registry = src.main.plugin_manager.get_registry()
    original = registry.get_api("memory")
    registry._apis["memory"] = fake_api

    try:
        resp = client.get("/plugins/digest")
    finally:
        registry._apis["memory"] = original

    assert resp.status_code == 200
    data = resp.json()
    assert data["user_name"] == "Bob"
    assert data["last_mood"] == "cheerful"
    assert data["people_count"] == 1
    assert data["conversation_count"] == 0
    assert len(data["active_projects"]) == 1
    assert data["active_projects"][0]["title"] == "My Project"
    assert data["active_projects"][0]["status"] == "active"
    assert "pending_questions" in data
