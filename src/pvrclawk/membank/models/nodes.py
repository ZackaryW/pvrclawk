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
    othermeta: dict[str, object] = Field(default_factory=dict)


class Feature(BaseNode):
    component: str
    test_scenario: str
    expected_result: str
    status: Status = Status.TODO
    othermeta: dict[str, object] = Field(default_factory=dict)


class Task(BaseNode):
    content: str
    status: Status = Status.TODO
    othermeta: dict[str, object] = Field(default_factory=dict)


class SubTask(BaseNode):
    content: str
    status: Status = Status.TODO
    othermeta: dict[str, object] = Field(default_factory=dict)


class Issue(BaseNode):
    content: str
    status: Status = Status.TODO
    othermeta: dict[str, object] = Field(default_factory=dict)


class Bug(BaseNode):
    content: str
    status: Status = Status.TODO
    othermeta: dict[str, object] = Field(default_factory=dict)


class Pattern(BaseNode):
    content: str
    pattern_type: str = ""


class Progress(BaseNode):
    content: str
    status: Status = Status.TODO


# Backward compatibility aliases during migration rollout.
class Active(Task):
    pass


class Archive(SubTask):
    pass
