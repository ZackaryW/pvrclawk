from dataclasses import dataclass
from pathlib import Path
import re

from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.base import BaseNode
from pvrclawk.membank.models.config import AppConfig
from pvrclawk.membank.models.link import Link


@dataclass
class BankContext:
    bank_id: str
    root: Path
    root_depth: int
    host_distance: int
    is_host: bool


class FederatedMembankService:
    def __init__(self, host_root: Path, config: AppConfig):
        self.host_root = host_root.resolve()
        self.config = config

    def discover_banks(self) -> list[BankContext]:
        discovery = self.config.federation.discovery
        git_root = self._find_git_root(
            start=self.host_root.parent,
            max_levels=discovery.max_git_lookup_levels,
        )
        if git_root is None and not discovery.allow_no_git_boundary:
            raise ValueError("Could not locate .git within configured lookup depth.")
        search_roots: list[Path] = [git_root] if git_root is not None else [self.host_root.parent]
        for external in discovery.external_roots:
            search_roots.append(Path(external).expanduser().resolve())

        candidates: set[Path] = set()
        for root in search_roots:
            if not root.exists():
                continue
            if discovery.only_dot_pvrclawk:
                for found in root.rglob(".pvrclawk"):
                    if found.is_dir():
                        candidates.add(found.resolve())
            for raw in discovery.candidate_paths:
                explicit = (root / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
                resolved = self._resolve_bank_root(explicit)
                if self._looks_like_membank_root(resolved):
                    candidates.add(resolved)

        candidates.add(self.host_root)
        contexts: list[BankContext] = []
        for candidate in sorted(candidates):
            if not self._looks_like_membank_root(candidate):
                continue
            owner = candidate.parent
            boundary = git_root if git_root is not None else owner
            root_depth = self._distance(owner, boundary)
            host_distance = self._distance(owner, self.host_root.parent)
            bank_id = owner.as_posix()
            contexts.append(
                BankContext(
                    bank_id=bank_id,
                    root=candidate,
                    root_depth=root_depth,
                    host_distance=host_distance,
                    is_host=candidate == self.host_root,
                )
            )
        return contexts

    def aggregate_for_focus(self, query_tags: list[str]) -> tuple[list[BaseNode], list[Link], dict[str, float]]:
        contexts = self.discover_banks()
        all_nodes: list[BaseNode] = []
        all_links: list[Link] = []
        multipliers: dict[str, float] = {}
        nodes_by_bank: dict[str, list[BaseNode]] = {}
        for ctx in contexts:
            storage = StorageEngine(ctx.root)
            nodes = storage.all_nodes()
            links = storage.all_links()
            all_nodes.extend(nodes)
            all_links.extend(links)
            nodes_by_bank[ctx.bank_id] = nodes
            multiplier = self._bank_multiplier(ctx)
            for node in nodes:
                multipliers[node.uid] = max(multipliers.get(node.uid, 0.0), multiplier)

        cross_links = self._build_cross_bank_links(nodes_by_bank, query_tags)
        all_links.extend(cross_links)
        return all_nodes, all_links, multipliers

    def aggregate_nodes(self, node_type: str | None = None) -> list[BaseNode]:
        nodes: list[BaseNode] = []
        for ctx in self.discover_banks():
            storage = StorageEngine(ctx.root)
            if node_type is None:
                nodes.extend(storage.all_nodes())
            else:
                nodes.extend(storage.load_nodes_by_type(node_type))
        return nodes

    def aggregate_node_by_uid(self, uid_or_prefix: str) -> BaseNode | None:
        matches: list[BaseNode] = []
        for ctx in self.discover_banks():
            storage = StorageEngine(ctx.root)
            resolved, reason = storage.resolve_uid_with_reason(uid_or_prefix)
            if reason in {"exact", "prefix"} and resolved is not None:
                node = storage.load_node(resolved)
                if node is not None:
                    matches.append(node)
        if len(matches) > 1:
            raise ValueError(f"Ambiguous UID prefix across federated banks: {uid_or_prefix}")
        return matches[0] if matches else None

    def aggregate_links_by_source_uid(self, uid_or_prefix: str) -> list[Link]:
        matches: list[tuple[StorageEngine, str]] = []
        for ctx in self.discover_banks():
            storage = StorageEngine(ctx.root)
            resolved, reason = storage.resolve_uid_with_reason(uid_or_prefix)
            if reason in {"exact", "prefix"} and resolved is not None:
                matches.append((storage, resolved))
        if len(matches) > 1:
            raise ValueError(f"Ambiguous UID prefix across federated banks: {uid_or_prefix}")
        if not matches:
            raise ValueError(f"Could not resolve UID reference: {uid_or_prefix}")
        storage, resolved = matches[0]
        return storage.load_links([resolved])

    def _bank_multiplier(self, ctx: BankContext) -> float:
        scoring = self.config.federation.scoring
        root_factor = scoring.root_importance_base / (1.0 + scoring.root_distance_decay * float(ctx.root_depth))
        host_factor = scoring.host_relevance_base / (1.0 + scoring.host_distance_decay * float(ctx.host_distance))
        path_penalty = self._bank_path_penalty_multiplier(ctx.bank_id)
        return max(root_factor * host_factor * path_penalty, 0.0)

    def _bank_path_penalty_multiplier(self, bank_path: str) -> float:
        multiplier = 1.0
        for rule in self.config.federation.scoring.bank_path_penalties:
            pattern = rule.pattern if hasattr(rule, "pattern") else str(rule.get("pattern", ""))
            rule_multiplier = rule.multiplier if hasattr(rule, "multiplier") else float(rule.get("multiplier", 1.0))
            try:
                if pattern and re.search(pattern, bank_path):
                    multiplier *= float(rule_multiplier)
            except re.error:
                continue
        return max(multiplier, 0.0)

    def _build_cross_bank_links(self, nodes_by_bank: dict[str, list[BaseNode]], query_tags: list[str]) -> list[Link]:
        if not query_tags:
            return []
        scoring = self.config.federation.scoring
        host_bank_id = self.host_root.parent.as_posix()
        host_nodes = nodes_by_bank.get(host_bank_id, [])
        query_set = set(query_tags)
        links: list[Link] = []
        for bank_id, remote_nodes in nodes_by_bank.items():
            if bank_id == host_bank_id:
                continue
            for host in host_nodes:
                host_tags = set(host.tags.keys())
                for remote in remote_nodes:
                    overlap = query_set & host_tags & set(remote.tags.keys())
                    if not overlap:
                        continue
                    weight = scoring.cross_bank_link_weight * float(len(overlap))
                    links.append(
                        Link(
                            source=host.uid,
                            target=remote.uid,
                            tags=sorted(overlap),
                            weight=weight,
                        )
                    )
                    links.append(
                        Link(
                            source=remote.uid,
                            target=host.uid,
                            tags=sorted(overlap),
                            weight=weight,
                        )
                    )
        return links

    def _find_git_root(self, start: Path, max_levels: int) -> Path | None:
        current = start.resolve()
        for _ in range(max_levels + 1):
            if (current / ".git").exists():
                return current
            if current.parent == current:
                break
            current = current.parent
        return None

    def _resolve_bank_root(self, root_path: Path) -> Path:
        path = Path(root_path)
        if path.name == ".pvrclawk":
            return path
        if self._looks_like_membank_root(path):
            return path
        return path / ".pvrclawk"

    def _looks_like_membank_root(self, path: Path) -> bool:
        return (
            (path / "nodes").exists()
            and (path / "index.json").exists()
            and (path / "links.json").exists()
        )

    def _distance(self, left: Path, right: Path) -> int:
        left_parts = left.resolve().parts
        right_parts = right.resolve().parts
        common = 0
        for lpart, rpart in zip(left_parts, right_parts):
            if lpart != rpart:
                break
            common += 1
        return (len(left_parts) - common) + (len(right_parts) - common)
