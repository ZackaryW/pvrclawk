from pydantic import Field

from pvrclawk.membank.models.base import BaseNode
from pvrclawk.membank.models.types import Status


class Memory(BaseNode):
    content: str


class MemoryLink(BaseNode):
    title: str
    summary: str
    file_path: str


class Story(BaseNode):
    role: str
    benefit: str
    criteria: list[str] = Field(default_factory=list)
    status: Status = Status.TODO


class Feature(BaseNode):
    component: str
    test_scenario: str
    expected_result: str
    status: Status = Status.TODO


class Active(BaseNode):
    content: str
    focus_area: str = ""


class Archive(BaseNode):
    content: str
    archived_from: str = ""
    reason: str = ""


class Pattern(BaseNode):
    content: str
    pattern_type: str = ""


class Progress(BaseNode):
    content: str
    status: Status = Status.TODO
