from pathlib import Path
import re
from datetime import datetime, timedelta, timezone

from pvrclawk.utils.config import AppConfig, load_config, write_config
from pvrclawk.utils.json_io import read_json, write_json
from pvrclawk.utils.session_store import resolve_session_bucket
from pvrclawk.membank.models.index import ClusterMeta, IndexData
from pvrclawk.membank.models.link import Link
from pvrclawk.membank.models.nodes import (
    Active,
    Archive,
    Bug,
    Feature,
    Issue,
    Memory,
    MemoryLink,
    Pattern,
    Progress,
    SubTask,
    Story,
    Task,
)
from pvrclawk.membank.models.session import Session, SessionIndex
from pvrclawk.membank.core.storage.index import add_unique
from pvrclawk.membank.core.storage.cluster import derive_cluster_name


class StorageEngine:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.nodes_dir = self.root / "nodes"
        self.additional_memory_dir = self.root / "additional_memory"
        self.index_file = self.root / "index.json"
        self.links_file = self.root / "links.json"
        self.rules_file = self.root / "rules.json"
        self.mood_file = self.root / "mood.json"
        self.session_bucket = resolve_session_bucket(self.root)
        self.sessions_dir = self.session_bucket
        self.session_index_file = self.session_bucket / "index.json"
        self.config_file = self.root / "config.toml"

    def _write_json(self, path: Path, data) -> None:
        write_json(path, data)

    def _read_json(self, path: Path, default):
        return read_json(path, default)

    def init_db(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.nodes_dir.mkdir(parents=True, exist_ok=True)
        self.additional_memory_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        if not self.index_file.exists():
            self._write_json(
                self.index_file,
                {"tags": {}, "types": {}, "uid_file": {}, "links_in": {}, "clusters": {}},
            )
        if not self.links_file.exists():
            self._write_json(self.links_file, {})
        if not self.rules_file.exists():
            self._write_json(self.rules_file, {"rules": []})
        if not self.mood_file.exists():
            self._write_json(self.mood_file, {})
        inbox = self.nodes_dir / "_inbox.json"
        if not inbox.exists():
            self._write_json(inbox, {})
        if not self.config_file.exists():
            write_config(self.config_file, AppConfig())
        self._ensure_runtime_state_gitignore()
        if not self.session_index_file.exists():
            self.save_session_index(SessionIndex())
        self._migrate_legacy_session_if_needed()

    def _session_path(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_id}.json"

    def load_session_index(self) -> SessionIndex:
        payload = self._read_json(self.session_index_file, {})
        if not isinstance(payload, dict) or not payload:
            return SessionIndex()
        if "active_session_id" not in payload and "session_ids" not in payload:
            return SessionIndex()
        try:
            return SessionIndex.model_validate(payload)
        except Exception:
            return SessionIndex()

    def save_session_index(self, index: SessionIndex) -> None:
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._write_json(self.session_index_file, index.model_dump(mode="json"))

    def _set_active_session_id(self, session_id: str | None) -> SessionIndex:
        index = self.load_session_index()
        if session_id is None:
            index.active_session_id = None
            self.save_session_index(index)
            return index
        if session_id in index.session_ids:
            index.session_ids.remove(session_id)
        index.session_ids.insert(0, session_id)
        index.active_session_id = session_id
        self.save_session_index(index)
        return index

    def load_session(self, session_id: str | None = None) -> Session | None:
        sid = session_id
        if sid is None:
            sid = self.load_session_index().active_session_id
        if not sid:
            return None
        path = self._session_path(sid)
        if not path.exists():
            return None
        payload = self._read_json(path, {})
        if not isinstance(payload, dict) or not payload:
            return None
        try:
            return Session.model_validate(payload)
        except Exception:
            return None

    def save_session(self, session: Session) -> None:
        path = self._session_path(session.session_id)
        self._write_json(path, session.model_dump(mode="json"))
        index = self.load_session_index()
        if session.session_id not in index.session_ids:
            index.session_ids.insert(0, session.session_id)
            self.save_session_index(index)

    def clear_session(self, session_id: str | None = None) -> bool:
        index = self.load_session_index()
        target_id = session_id or index.active_session_id
        if target_id is None:
            return False
        removed = False
        target_path = self._session_path(target_id)
        if target_path.exists():
            target_path.unlink()
            removed = True
        if target_id in index.session_ids:
            index.session_ids.remove(target_id)
            removed = True
        if index.active_session_id == target_id:
            index.active_session_id = index.session_ids[0] if index.session_ids else None
            removed = True
        self.save_session_index(index)
        return removed

    def is_session_expired(self, session: Session, max_age_days: int = 2) -> bool:
        return datetime.now(timezone.utc) - session.created_at > timedelta(days=max_age_days)

    def load_active_session(self, max_age_days: int = 2) -> Session | None:
        index = self.load_session_index()
        active_id = index.active_session_id
        if active_id is None:
            return None
        session = self.load_session(active_id)
        if session is None:
            # Auto-recover missing referenced session by recreating it.
            session = Session(session_id=active_id)
            self.save_session(session)
            self._set_active_session_id(active_id)
            return session
        if session is None:
            return None
        if self.is_session_expired(session, max_age_days=max_age_days):
            self.clear_session(session.session_id)
            return None
        return session

    def activate_session(self, session_id: str | None = None) -> Session:
        self.init_db()
        if session_id:
            existing = self.load_session(session_id)
            if existing is not None and not self.is_session_expired(existing):
                self._set_active_session_id(existing.session_id)
                return existing
            session = Session(session_id=session_id)
            self.save_session(session)
            self._set_active_session_id(session.session_id)
            return session

        existing_active = self.load_active_session()
        if existing_active is not None:
            self._set_active_session_id(existing_active.session_id)
            return existing_active

        session = Session()
        self.save_session(session)
        self._set_active_session_id(session.session_id)
        return session

    def reset_session(self, session_id: str | None = None) -> Session:
        target_id = session_id or self.load_session_index().active_session_id
        session = self.activate_session(session_id=target_id)
        session.served_uids = []
        self.save_session(session)
        self._set_active_session_id(session.session_id)
        return session

    def record_session_served(self, session: Session, uids: list[str]) -> Session:
        seen = set(session.served_uids)
        for uid in uids:
            if uid not in seen:
                session.served_uids.append(uid)
                seen.add(uid)
        self.save_session(session)
        return session

    def _migrate_legacy_session_if_needed(self) -> None:
        # Legacy local files under .pvrclawk/ are migrated into user-level session storage.
        legacy_index_file = self.root / "session.json"
        legacy_recent_file = self.root / "recent_uid.json"
        index = self.load_session_index()

        if legacy_index_file.exists():
            payload = self._read_json(legacy_index_file, {})
            if isinstance(payload, dict) and payload:
                # Legacy single-session payload
                if "session_id" in payload and "active_session_id" not in payload and "session_ids" not in payload:
                    try:
                        session = Session.model_validate(payload)
                        self.save_session(session)
                        self._set_active_session_id(session.session_id)
                        index = self.load_session_index()
                    except Exception:
                        pass
                # Transitional local multi-session index payload
                elif "active_session_id" in payload or "session_ids" in payload:
                    try:
                        legacy_index = SessionIndex.model_validate(payload)
                        for session_id in legacy_index.session_ids:
                            local_path = self.root / "sessions" / f"{session_id}.json"
                            if not local_path.exists():
                                continue
                            session_payload = self._read_json(local_path, {})
                            try:
                                session = Session.model_validate(session_payload)
                            except Exception:
                                continue
                            self.save_session(session)
                        if legacy_index.active_session_id:
                            self._set_active_session_id(legacy_index.active_session_id)
                        index = self.load_session_index()
                    except Exception:
                        pass

        # Seed legacy recent_uid.json into active session only if missing recent history.
        if legacy_recent_file.exists():
            legacy_recent = self._read_json(legacy_recent_file, [])
            active = self.load_active_session()
            if active is not None and isinstance(legacy_recent, list) and not active.recent_uids:
                active.recent_uids = [str(uid) for uid in legacy_recent[:10]]
                self.save_session(active)

        # Ensure index file exists even without any legacy artifacts.
        if not self.session_index_file.exists():
            self.save_session_index(index)

    def load_index(self) -> IndexData:
        return IndexData.model_validate(self._read_json(self.index_file, {}))

    def save_index(self, index: IndexData) -> None:
        self._write_json(self.index_file, index.model_dump())

    def save_node(self, node, node_type: str) -> str:
        index = self.load_index()

        # Auto-archive existing active nodes if config allows
        if node_type == "active":
            config = load_config(self.config_file)
            if config.auto_archive_active:
                self._archive_active_nodes(index)

        cluster_name = "_inbox"
        cluster_path = self.nodes_dir / f"{cluster_name}.json"
        cluster_data = self._read_json(cluster_path, {})
        payload = node.model_dump(mode="json")
        payload["__type__"] = node_type
        cluster_data[node.uid] = payload
        self._write_json(cluster_path, cluster_data)

        index.uid_file[node.uid] = cluster_name
        add_unique(index.types, node_type, node.uid)
        for tag in node.tags:
            add_unique(index.tags, tag, node.uid)
        if cluster_name not in index.clusters:
            index.clusters[cluster_name] = ClusterMeta(top_tags=[], size=0)
        index.clusters[cluster_name].size = len(cluster_data)
        self._record_recent_uid(node.uid)
        self.save_index(index)
        return node.uid

    def _archive_active_nodes(self, index: IndexData) -> None:
        """Convert all existing active nodes to archive type."""
        active_uids = list(index.types.get("active", []))
        if not active_uids:
            return
        # Group by cluster file
        by_cluster: dict[str, list[str]] = {}
        for uid in active_uids:
            cluster = index.uid_file.get(uid)
            if cluster:
                by_cluster.setdefault(cluster, []).append(uid)
        # Rewrite each affected cluster file
        for cname, uids in by_cluster.items():
            cluster_path = self.nodes_dir / f"{cname}.json"
            data = self._read_json(cluster_path, {})
            for uid in uids:
                payload = data.get(uid)
                if not payload:
                    continue
                payload["__type__"] = "archive"
                payload["archived_from"] = payload.get("focus_area", "active")
                payload["reason"] = "superseded by new active node"
                data[uid] = payload
            self._write_json(cluster_path, data)
        # Update index types
        for uid in active_uids:
            if uid in index.types.get("active", []):
                index.types["active"].remove(uid)
            add_unique(index.types, "archive", uid)

    def load_nodes(self, uids: list[str]):
        index = self.load_index()
        by_cluster: dict[str, list[str]] = {}
        for uid in uids:
            cluster = index.uid_file.get(uid)
            if not cluster:
                continue
            by_cluster.setdefault(cluster, []).append(uid)

        cls_map = {
            "memory": Memory,
            "memorylink": MemoryLink,
            "story": Story,
            "feature": Feature,
            "active": Task,
            "archive": SubTask,
            "task": Task,
            "subtask": SubTask,
            "issue": Issue,
            "bug": Bug,
            "pattern": Pattern,
            "progress": Progress,
        }
        out = []
        for cluster, cluster_uids in by_cluster.items():
            data = self._read_json(self.nodes_dir / f"{cluster}.json", {})
            for uid in cluster_uids:
                payload = data.get(uid)
                if not payload:
                    continue
                node_type = self._normalized_node_type(payload)
                payload = dict(payload)
                payload.pop("__type__", None)
                cls = cls_map.get(node_type, Memory)
                out.append(cls.model_validate(payload))
        return out

    def _normalized_node_type(self, payload: dict) -> str:
        raw = str(payload.get("__type__", "memory"))
        if raw == "active":
            raw = "task"
        elif raw == "archive":
            raw = "subtask"

        tags = {str(k).lower() for k in payload.get("tags", {}).keys()}
        blob_parts = [
            str(payload.get("content", "")),
            str(payload.get("title", "")),
            str(payload.get("summary", "")),
            str(payload.get("focus_area", "")),
            str(payload.get("archived_from", "")),
        ]
        blob = " ".join(blob_parts).lower()

        if raw in {"task", "subtask"}:
            if "bug" in tags or " bug" in f" {blob}":
                return "bug"
            if "issue" in tags or "jira" in tags or "proj-" in blob:
                return "issue"
        return raw

    def save_link(self, link: Link) -> str:
        self.save_links([link])
        return link.uid

    def save_links(self, links_to_save: list[Link]) -> int:
        if not links_to_save:
            return 0
        links = self._read_json(self.links_file, {})
        index = self.load_index()

        for link in links_to_save:
            links.setdefault(link.source, [])
            links[link.source].append(link.model_dump(mode="json"))
            add_unique(index.links_in, link.target, link.source)

        self._write_json(self.links_file, links)
        self.save_index(index)
        return len(links_to_save)

    def load_links(self, source_uids: list[str]) -> list[Link]:
        links = self._read_json(self.links_file, {})
        out: list[Link] = []
        for source in source_uids:
            for payload in links.get(source, []):
                out.append(Link.model_validate(payload))
        return out

    def adjust_link_weights_by_tags(self, tags: list[str], delta: float) -> int:
        links = self._read_json(self.links_file, {})
        updated = 0
        needed = set(tags)
        for source, items in links.items():
            for payload in items:
                existing = set(payload.get("tags", []))
                if needed.issubset(existing):
                    payload["weight"] = float(payload.get("weight", 1.0)) + delta
                    updated += 1
        self._write_json(self.links_file, links)
        return updated

    def load_node(self, uid: str):
        """Load a single node by UID. Returns None if not found."""
        results = self.load_nodes([uid])
        return results[0] if results else None

    def resolve_uid(self, uid_or_prefix: str) -> str | None:
        """Resolve an exact UID or unique UID prefix."""
        uid, reason = self.resolve_uid_with_reason(uid_or_prefix)
        if reason in {"exact", "prefix"}:
            return uid
        return None

    def resolve_uid_with_reason(self, uid_or_prefix: str) -> tuple[str | None, str]:
        """Resolve exact/prefix UID and return reason: exact|prefix|ambiguous|missing."""
        index = self.load_index()
        if uid_or_prefix in index.uid_file:
            return uid_or_prefix, "exact"
        matches = [uid for uid in index.uid_file if uid.startswith(uid_or_prefix)]
        if len(matches) == 1:
            return matches[0], "prefix"
        if len(matches) > 1:
            return None, "ambiguous"
        return None, "missing"

    def resolve_recent_uid(self, last: int) -> str | None:
        """Resolve UID by active-session recency index (1-based)."""
        if last < 1:
            return None
        active = self.load_active_session()
        if active is None:
            return None
        recent_uids = list(active.recent_uids)
        if last > len(recent_uids):
            return None
        return recent_uids[last - 1]

    def update_node_status(self, uid: str, status: str) -> bool:
        """Update the status field of a node. Returns True if updated."""
        index = self.load_index()
        cluster_name = index.uid_file.get(uid)
        if not cluster_name:
            return False
        cluster_path = self.nodes_dir / f"{cluster_name}.json"
        data = self._read_json(cluster_path, {})
        payload = data.get(uid)
        if not payload:
            return False
        if "status" not in payload:
            return False
        payload["status"] = status
        payload["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._write_json(cluster_path, data)
        self._touch_recent_uid(uid)
        return True

    def remove_node(self, uid: str) -> bool:
        """Remove a node by UID and clean related index/link references."""
        index = self.load_index()
        cluster_name = index.uid_file.get(uid)
        if not cluster_name:
            return False

        cluster_path = self.nodes_dir / f"{cluster_name}.json"
        cluster_data = self._read_json(cluster_path, {})
        payload = cluster_data.pop(uid, None)
        if payload is None:
            return False
        self._write_json(cluster_path, cluster_data)

        node_type = str(payload.get("__type__", "memory"))

        index.uid_file.pop(uid, None)
        self._remove_uid_from_all_session_recents(uid)

        type_uids = index.types.get(node_type, [])
        if uid in type_uids:
            type_uids.remove(uid)
        if not type_uids and node_type in index.types:
            index.types.pop(node_type, None)

        for tag in payload.get("tags", {}):
            tagged_uids = index.tags.get(tag, [])
            if uid in tagged_uids:
                tagged_uids.remove(uid)
            if not tagged_uids and tag in index.tags:
                index.tags.pop(tag, None)

        index.links_in.pop(uid, None)
        for target_uid, source_uids in list(index.links_in.items()):
            if uid in source_uids:
                source_uids.remove(uid)
            if not source_uids:
                index.links_in.pop(target_uid, None)

        if cluster_name in index.clusters:
            index.clusters[cluster_name].size = len(cluster_data)

        links = self._read_json(self.links_file, {})
        links.pop(uid, None)
        for source_uid, items in list(links.items()):
            kept = [item for item in items if item.get("target") != uid]
            if kept:
                links[source_uid] = kept
            else:
                links.pop(source_uid, None)
        self._write_json(self.links_file, links)

        self.save_index(index)
        return True

    def remove_nodes_by_type(self, node_type: str) -> int:
        """Remove all nodes of a given type."""
        index = self.load_index()
        uids = list(index.types.get(node_type, []))
        removed = 0
        for uid in uids:
            if self.remove_node(uid):
                removed += 1
        return removed

    def load_nodes_by_type(self, node_type: str):
        index = self.load_index()
        uids = index.types.get(node_type, [])
        return self.load_nodes(uids)

    def create_memory_file(self, title: str, content: str) -> Path:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "memory"
        path = self.additional_memory_dir / f"{slug}.md"
        if not path.exists():
            path.write_text(content, encoding="utf-8")
        return path

    def prune(self) -> str:
        inbox_path = self.nodes_dir / "_inbox.json"
        inbox = self._read_json(inbox_path, {})
        if not inbox:
            return "_inbox"

        tag_weights: dict[str, float] = {}
        for payload in inbox.values():
            for tag, weight in payload.get("tags", {}).items():
                tag_weights[tag] = tag_weights.get(tag, 0.0) + float(weight)
        cluster_name = derive_cluster_name(tag_weights)
        cluster_path = self.nodes_dir / f"{cluster_name}.json"
        existing = self._read_json(cluster_path, {})
        existing.update(inbox)
        self._write_json(cluster_path, existing)
        self._write_json(inbox_path, {})

        # rebuild lightweight index maps from cluster files
        index = IndexData()
        for f in self.nodes_dir.glob("*.json"):
            if f.name == "_inbox.json":
                continue
            data = self._read_json(f, {})
            cname = f.stem
            index.clusters[cname] = ClusterMeta(top_tags=list(tag_weights.keys())[:3], size=len(data))
            for uid, payload in data.items():
                index.uid_file[uid] = cname
                ntype = payload.get("__type__", "memory")
                add_unique(index.types, ntype, uid)
                for tag in payload.get("tags", {}):
                    add_unique(index.tags, tag, uid)

        # rebuild links_in from links.json
        raw_links = self._read_json(self.links_file, {})
        for source, items in raw_links.items():
            for payload in items:
                target = payload.get("target", "")
                if target:
                    add_unique(index.links_in, target, source)

        self.save_index(index)
        self._prune_session_recent_uids(set(index.uid_file.keys()))
        return cluster_name

    def _touch_recent_uid(self, uid: str) -> None:
        index = self.load_index()
        if uid not in index.uid_file:
            return
        self._record_recent_uid(uid)

    def _record_recent_uid(self, uid: str) -> None:
        active = self.load_active_session()
        if active is None:
            return
        if uid in active.recent_uids:
            active.recent_uids.remove(uid)
        active.recent_uids.insert(0, uid)
        active.recent_uids = active.recent_uids[:10]
        self.save_session(active)

    def _remove_uid_from_all_session_recents(self, uid: str) -> None:
        index = self.load_session_index()
        changed = False
        for session_id in list(index.session_ids):
            session = self.load_session(session_id)
            if session is None:
                continue
            if uid in session.recent_uids:
                session.recent_uids = [item for item in session.recent_uids if item != uid]
                self.save_session(session)
                changed = True
        if changed:
            self.save_session_index(index)

    def _prune_session_recent_uids(self, valid_uids: set[str]) -> None:
        index = self.load_session_index()
        for session_id in list(index.session_ids):
            session = self.load_session(session_id)
            if session is None:
                continue
            filtered = [uid for uid in session.recent_uids if uid in valid_uids]
            if filtered != session.recent_uids:
                session.recent_uids = filtered
                self.save_session(session)

    def _ensure_runtime_state_gitignore(self) -> None:
        # Session runtime state now lives in user-level config storage, not project files.
        return

    def all_nodes(self):
        index = self.load_index()
        return self.load_nodes(list(index.uid_file.keys()))

    def all_links(self) -> list[Link]:
        raw = self._read_json(self.links_file, {})
        out: list[Link] = []
        for items in raw.values():
            for payload in items:
                out.append(Link.model_validate(payload))
        return out

    def add_rule(self, rule: str) -> None:
        data = self._read_json(self.rules_file, {"rules": []})
        data.setdefault("rules", [])
        data["rules"].append(rule)
        self._write_json(self.rules_file, data)

    def list_rules(self) -> list[str]:
        data = self._read_json(self.rules_file, {"rules": []})
        return list(data.get("rules", []))
