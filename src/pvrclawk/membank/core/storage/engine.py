from pathlib import Path
import json
import re

from pvrclawk.membank.core.config import write_config
from pvrclawk.membank.models.config import AppConfig
from pvrclawk.membank.models.index import ClusterMeta, IndexData
from pvrclawk.membank.models.link import Link
from pvrclawk.membank.models.nodes import (
    Active,
    Archive,
    Feature,
    Memory,
    MemoryLink,
    Pattern,
    Progress,
    Story,
)
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
        self.config_file = self.root / "config.toml"

    def _write_json(self, path: Path, data) -> None:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _read_json(self, path: Path, default):
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def init_db(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.nodes_dir.mkdir(parents=True, exist_ok=True)
        self.additional_memory_dir.mkdir(parents=True, exist_ok=True)
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

    def load_index(self) -> IndexData:
        return IndexData.model_validate(self._read_json(self.index_file, {}))

    def save_index(self, index: IndexData) -> None:
        self._write_json(self.index_file, index.model_dump())

    def save_node(self, node, node_type: str) -> str:
        index = self.load_index()
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
        self.save_index(index)
        return node.uid

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
            "active": Active,
            "archive": Archive,
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
                node_type = payload.pop("__type__", "memory")
                cls = cls_map.get(node_type, Memory)
                out.append(cls.model_validate(payload))
        return out

    def save_link(self, link: Link) -> str:
        links = self._read_json(self.links_file, {})
        links.setdefault(link.source, [])
        links[link.source].append(link.model_dump(mode="json"))
        self._write_json(self.links_file, links)

        index = self.load_index()
        add_unique(index.links_in, link.target, link.source)
        self.save_index(index)
        return link.uid

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
        self.save_index(index)
        return cluster_name

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
