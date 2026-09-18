import asyncio
import sqlite3
from datetime import datetime, timezone

from fastapi import APIRouter


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _count_rows(conn, table: str, vault_name: str) -> int:
    """Count rows in another plugin's table. Returns 0 when the table does
    not exist (soft dependency on chat is not installed)."""
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (table,)
    ).fetchone()
    if row is None:
        return 0
    return conn.execute(
        f"SELECT COUNT(*) FROM {table} WHERE vault_name = ?", (vault_name,)
    ).fetchone()[0]


class Plugin:
    def on_load(self, ctx):
        self._vault = ctx.vault_manager
        self._db = ctx.db_module
        self._ctx = ctx

        router = APIRouter()

        @router.get("")
        async def digest():
            vn = self._ctx.vault_name
            result = await asyncio.to_thread(self._build_digest, vn)
            self._ctx.store.set("digest_refreshed_at", _now_utc())
            return result

        ctx.register_router(router)

        def _on_diary_saved(payload):
            self._ctx.store.set("digest_data_updated_at", _now_utc())

        ctx.on_event("diary_saved", _on_diary_saved)

    def _build_digest(self, vault_name: str) -> dict:
        vault = self._vault.vault_path(vault_name)

        projects = []
        proj_dir = vault / "Projects"
        if proj_dir.is_dir():
            for f in proj_dir.glob("*.md"):
                content = f.read_text(encoding="utf-8")
                status = self._vault.extract_frontmatter_field(content, "status") or "unknown"
                title = self._vault.extract_frontmatter_field(content, "title") or f.stem
                if status != "archived":
                    projects.append({"title": title, "status": status})

        questions = ""
        memory_api = self._ctx.get_plugin_api("memory")
        if memory_api and hasattr(memory_api, "get_watch_fors"):
            questions = memory_api.get_watch_fors(vault_name) or ""

        people_count = 0
        user_name = "friend"
        if memory_api:
            people = memory_api.get_people(vault_name)
            people_count = len(people)
            facts = memory_api.get_facts(vault_name)
            for fact in facts:
                if fact.get("key") == "name":
                    user_name = fact["value"]
                    break

        conn = self._db.get_db()
        convos_count = _count_rows(conn, "chat_threads", vault_name)

        last_mood = None
        diary_dir = vault / "Diary"
        if diary_dir.is_dir():
            for f in sorted(diary_dir.glob("*.md"), reverse=True):
                content = f.read_text(encoding="utf-8")
                mood = self._vault.extract_frontmatter_field(content, "mood")
                if mood:
                    last_mood = mood
                    break

        return {
            "user_name": user_name,
            "last_mood": last_mood,
            "active_projects": projects,
            "pending_questions": questions or "(nothing pending)",
            "people_count": people_count,
            "conversation_count": convos_count,
        }
