from pydantic import BaseModel, Field


class ClusterMeta(BaseModel):
    top_tags: list[str] = Field(default_factory=list)
    size: int = 0


class IndexData(BaseModel):
    tags: dict[str, list[str]] = Field(default_factory=dict)
    types: dict[str, list[str]] = Field(default_factory=dict)
    uid_file: dict[str, str] = Field(default_factory=dict)
    links_in: dict[str, list[str]] = Field(default_factory=dict)
    clusters: dict[str, ClusterMeta] = Field(default_factory=dict)
