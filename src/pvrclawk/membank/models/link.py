import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Link(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    target: str
    tags: list[str] = Field(default_factory=list)
    weight: float = 1.0
    decay: float = 1.0
    usage_count: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
