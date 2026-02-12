from enum import Enum


class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class NodeType(str, Enum):
    MEMORY = "memory"
    MEMORYLINK = "memorylink"
    STORY = "story"
    FEATURE = "feature"
    ACTIVE = "active"
    ARCHIVE = "archive"
    PATTERN = "pattern"
    PROGRESS = "progress"
