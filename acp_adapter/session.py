# -*- coding: utf-8 -*-
"""acp_adapter/session.py — ACP oturum yoneticisi (SessionManager + SessionState)."""
from __future__ import annotations

import copy
import json
import re
import sys
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any

from ReYMeN_state import SessionDB

import ReYMeN_constants as _rc

def _is_wsl() -> bool:
    """Check if running under WSL — uses _wsl_detected for monkeypatching."""
    if getattr(_rc, "_wsl_detected", None) is not None:
        return bool(_rc._wsl_detected)
    return _rc.is_wsl()


# ---------------------------------------------------------------------------
# SessionState — per-session in-memory state
# ---------------------------------------------------------------------------

@dataclass
class SessionState:
    """In-memory state for a single ACP session."""
    session_id: str
    cwd: str = ""
    history: list[dict[str, Any]] = field(default_factory=list)
    agent: Any = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _translate_acp_cwd(path: str) -> str:
    """Translate Windows drive-letter paths to /mnt/x/... when running under WSL."""
    if not _is_wsl():
        return path
    # Already a POSIX /mnt/x path?
    if path.startswith("/mnt/") and len(path) > 5 and path[5] == "/":
        return path
    # E:\Projects → /mnt/e/Projects
    m = re.match(r"^([A-Za-z]):[/\\](.*)", path)
    if m:
        drive = m.group(1).lower()
        rest = m.group(2).replace("\\", "/")
        return f"/mnt/{drive}/{rest}"
    # D:/work/project → /mnt/d/work/project
    m = re.match(r"^([A-Za-z]):/(.*)", path)
    if m:
        drive = m.group(1).lower()
        rest = m.group(2)
        return f"/mnt/{drive}/{rest}"
    return path


def _register_task_cwd(task_id: str, cwd: str) -> None:
    """Register cwd override for terminal tool when running under WSL."""
    try:
        from tools.terminal_tool import register_task_env_overrides
        if _is_wsl():
            overrides: dict[str, str] = {}
            # Translate Windows drive path to WSL mount
            m = re.match(r"^([A-Za-z]):[/\\](.*)", cwd)
            if m:
                drive = m.group(1).lower()
                rest = m.group(2).replace("\\", "/")
                overrides["cwd"] = f"/mnt/{drive}/{rest}"
            if overrides:
                register_task_env_overrides(task_id, overrides)
    except ImportError:
        pass


# ---------------------------------------------------------------------------
# SessionManager
# ---------------------------------------------------------------------------

class SessionManager:
    """ACP session manager backed by SessionDB for persistence."""

    def __init__(self, agent_factory=None, db: SessionDB | None = None):
        self._sessions: dict[str, SessionState] = {}
        self._known_session_ids: set[str] = set()  # sessions created/restored by this manager
        self._lock = threading.Lock()
        self._db = db or SessionDB()
        self._agent_factory = agent_factory

    # -- internal helpers ---------------------------------------------------

    def _get_db(self) -> SessionDB:
        return self._db

    def _make_agent(self, **kwargs) -> Any:
        """Create an agent instance (factory or real AIAgent)."""
        if self._agent_factory:
            return self._agent_factory(**kwargs)
        from run_agent import AIAgent
        return AIAgent(**kwargs)

    def _restore_from_db(self, session_id: str) -> SessionState | None:
        """Restore a session from DB if it's an ACP session not in memory."""
        row = self._db.get_session(session_id)
        if row is None:
            return None
        if row.get("source") != "acp":
            return None
        # Reconstruct cwd from model_config JSON
        cwd = ""
        mc_raw = row.get("model_config")
        if mc_raw:
            try:
                mc = json.loads(mc_raw)
                cwd = mc.get("cwd", "")
            except (json.JSONDecodeError, TypeError):
                pass
        # Restore messages
        messages = self._db.get_messages_as_conversation(session_id) or []
        # Restore provider snapshot from model_config
        provider_snapshot: dict[str, Any] = {}
        if mc_raw:
            try:
                mc = json.loads(mc_raw)
                provider_snapshot = mc.get("provider_snapshot", {})
            except (json.JSONDecodeError, TypeError):
                pass
        # Create agent
        agent = self._make_agent(**provider_snapshot) if provider_snapshot else self._make_agent()
        state = SessionState(
            session_id=session_id,
            cwd=cwd,
            history=messages,
            agent=agent,
        )
        with self._lock:
            self._sessions[session_id] = state
        return state

    # -- public API ---------------------------------------------------------

    def create_session(self, cwd: str | None = None) -> SessionState:
        """Create a new ACP session."""
        session_id = str(uuid.uuid4())
        translated_cwd = _translate_acp_cwd(cwd) if cwd else ""
        _register_task_cwd(session_id, translated_cwd)

        agent = self._make_agent()
        state = SessionState(
            session_id=session_id,
            cwd=translated_cwd,
            agent=agent,
        )
        with self._lock:
            self._sessions[session_id] = state
            self._known_session_ids.add(session_id)

        # Persist to DB
        try:
            agent_model = str(getattr(agent, "model", "default")) if hasattr(agent, "model") else "default"
            self._db.create_session(
                session_id=session_id,
                source="acp",
                model=agent_model,
                model_config={"cwd": translated_cwd},
            )
        except Exception:
            pass

        return state

    def get_session(self, session_id: str) -> SessionState | None:
        """Get session by ID, restoring from DB if needed."""
        with self._lock:
            if session_id in self._sessions:
                return self._sessions[session_id]
        # Try DB restore
        return self._restore_from_db(session_id)

    def fork_session(self, session_id: str, cwd: str | None = None) -> SessionState | None:
        """Fork a session — deep copy history, new ID."""
        source = self.get_session(session_id)
        if source is None:
            return None
        new_id = str(uuid.uuid4())
        new_cwd = _translate_acp_cwd(cwd) if cwd else source.cwd
        history_copy = copy.deepcopy(source.history)
        agent = self._make_agent()
        state = SessionState(
            session_id=new_id,
            cwd=new_cwd,
            history=history_copy,
            agent=agent,
        )
        with self._lock:
            self._sessions[new_id] = state
        # Persist
        try:
            agent_model = str(getattr(agent, "model", "default")) if hasattr(agent, "model") else "default"
            self._db.create_session(
                session_id=new_id,
                source="acp",
                model=agent_model,
                model_config={"cwd": new_cwd},
            )
        except Exception:
            pass
        return state

    def update_cwd(self, session_id: str, cwd: str) -> SessionState | None:
        """Update a session's cwd."""
        state = self.get_session(session_id)
        if state is None:
            return None
        translated = _translate_acp_cwd(cwd)
        state.cwd = translated
        # Persist
        try:
            self._update_model_config(session_id, {"cwd": translated})
        except Exception:
            pass
        return state

    def list_sessions(self, cwd: str | None = None) -> list[dict]:
        """List sessions (with non-empty history), optionally filtered by cwd."""
        results: list[dict] = []
        seen: set[str] = set()

        # Pre-load DB metadata for in-memory enrichment
        _db_meta: dict[str, dict] = {}
        try:
            for row in self._db.list_sessions_rich(source="acp"):
                ts = str(row.get("last_active", ""))
                _db_meta[row["id"]] = {
                    "last_active": ts,
                    "title": row.get("title", ""),
                    "preview": row.get("preview", ""),
                }
        except Exception:
            pass

        # In-memory sessions — enrich with DB metadata for sorting/titles
        with self._lock:
            for sid, state in self._sessions.items():
                if not state.history:
                    continue
                seen.add(sid)
                if cwd and not self._cwd_matches(state.cwd, cwd):
                    continue
                meta = _db_meta.get(sid, {})
                # Prefer DB title > history preview
                title = meta.get("title") or meta.get("preview") or (
                    state.history[0].get("content", "")[:60] if state.history else ""
                )
                updated = meta.get("last_active", "")
                results.append({
                    "session_id": sid,
                    "cwd": state.cwd,
                    "title": title,
                    "updated_at": updated,
                })

        # DB-only sessions
        try:
            db_rows = self._db.list_sessions_rich(source="acp")
            for row in db_rows:
                sid = row["id"]
                if sid in seen:
                    continue
                if not row.get("message_count", 0):
                    continue
                db_cwd = row.get("cwd") or ""
                mc_raw = row.get("model_config")
                if mc_raw and not db_cwd:
                    try:
                        mc = json.loads(mc_raw)
                        db_cwd = mc.get("cwd", "")
                    except (json.JSONDecodeError, TypeError):
                        pass
                if cwd and not self._cwd_matches(db_cwd, cwd):
                    continue
                title = row.get("title") or row.get("preview", "")
                updated = str(row.get("last_active", ""))
                results.append({
                    "session_id": sid,
                    "cwd": db_cwd,
                    "title": title,
                    "updated_at": updated,
                })
        except Exception:
            pass

        # Sort by updated_at desc (newer first)
        results.sort(key=lambda r: r.get("updated_at", ""), reverse=True)
        return results

    def save_session(self, session_id: str) -> None:
        """Persist session history to DB."""
        state = self.get_session(session_id)
        if state is None:
            return
        try:
            self._db.replace_messages(session_id, state.history)
        except Exception:
            pass

    def cleanup(self) -> None:
        """Remove all sessions."""
        with self._lock:
            sids = list(self._sessions.keys())
            for sid in sids:
                del self._sessions[sid]
                try:
                    self._db.delete_session(sid)
                except Exception:
                    pass

    def remove_session(self, session_id: str) -> bool:
        """Remove a single session. Returns True if removed, False if not found."""
        removed = False
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                removed = True
        # Check DB
        try:
            row = self._db.get_session(session_id)
            if row is not None:
                self._db.delete_session(session_id)
                removed = True
        except Exception:
            pass
        return removed

    # -- internal -----------------------------------------------------------

    def _cwd_matches(self, stored_cwd: str, query_cwd: str) -> bool:
        """Check if stored_cwd matches query_cwd (including WSL/Windows cross-match)."""
        if stored_cwd == query_cwd:
            return True
        # WSL /mnt/e/... matches Windows E:\...
        if re.match(r"^/mnt/([a-z])/(.*)", stored_cwd):
            m = re.match(r"^/mnt/([a-z])/(.*)", stored_cwd)
            rest_slashed = m.group(2).replace("/", "\\")
            win_path = f"{m.group(1).upper()}:\\{rest_slashed}"
            if win_path.lower() == query_cwd.lower():
                return True
            win_fwd = f"{m.group(1).upper()}:/{m.group(2)}"
            if win_fwd.lower() == query_cwd.lower():
                return True
        # Reverse: stored Windows, query WSL
        if re.match(r"^[A-Za-z]:[/\\]", stored_cwd):
            m = re.match(r"^([A-Za-z]):[/\\](.*)", stored_cwd)
            wsl_path = f"/mnt/{m.group(1).lower()}/{m.group(2).replace(chr(92), '/')}"
            if wsl_path.lower() == query_cwd.lower():
                return True
        return False

    def _update_model_config(self, session_id: str, updates: dict) -> None:
        """Merge updates into the session's model_config JSON in DB."""
        row = self._db.get_session(session_id)
        if row is None:
            return
        mc = {}
        mc_raw = row.get("model_config")
        if mc_raw:
            try:
                mc = json.loads(mc_raw)
            except (json.JSONDecodeError, TypeError):
                pass
        mc.update(updates)
        new_config = json.dumps(mc)

        def _do(conn):
            conn.execute(
                "UPDATE sessions SET model_config = ? WHERE id = ?",
                (new_config, session_id),
            )
        self._db._execute_write(_do)


# Backward compat alias
SessionYoneticisi = SessionManager
