from pvrclawk.membank.models.index import ClusterMeta, IndexData


def add_unique(mapping: dict[str, list[str]], key: str, value: str) -> None:
    values = mapping.setdefault(key, [])
    if value not in values:
        values.append(value)


def remove_value(mapping: dict[str, list[str]], key: str, value: str) -> None:
    values = mapping.get(key, [])
    if value in values:
        values.remove(value)
    if not values and key in mapping:
        del mapping[key]


def ensure_cluster(index: IndexData, cluster_name: str) -> None:
    if cluster_name not in index.clusters:
        index.clusters[cluster_name] = ClusterMeta(top_tags=[], size=0)
