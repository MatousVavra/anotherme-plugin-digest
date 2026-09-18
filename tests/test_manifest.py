from pathlib import Path

import yaml

MANIFEST = Path(__file__).resolve().parents[1] / "plugin" / "plugin.yaml"


def test_hard_and_soft_dependencies():
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert data["dependencies"] == ["memory"]
    soft = {d["name"]: d.get("enables", "") for d in data["soft_dependencies"]}
    assert soft == {"chat": "conversation count in digest"}


def test_manifest_declares_ui_tab():
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert data["ui"]["tab"] == "Digest"
    assert data["ui"]["icon"] == "sun"
    assert data["ui"]["order"] == 95
    assert "ui" in data["capabilities"]


def test_manifest_has_no_dead_schedule_setting():
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert data.get("settings", []) == []
