import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class BaseNode(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tags: dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def add_tag(self, name: str, weight: float = 1.0) -> None:
        self.tags[name] = weight
