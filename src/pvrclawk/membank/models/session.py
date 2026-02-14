import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Session(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    served_uids: list[str] = Field(default_factory=list)
    recent_uids: list[str] = Field(default_factory=list)


class SessionIndex(BaseModel):
    active_session_id: str | None = None
    session_ids: list[str] = Field(default_factory=list)
