from pvrclawk.membank.models.types import NodeType, Status


def test_types_values():
    assert NodeType.MEMORY.value == "memory"
    assert NodeType.MEMORYLINK.value == "memorylink"
    assert NodeType.ISSUE.value == "issue"
    assert NodeType.BUG.value == "bug"
    assert NodeType.TASK.value == "task"
    assert NodeType.SUBTASK.value == "subtask"
    assert Status.TODO.value == "todo"
