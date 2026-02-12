from pvrclawk.membank.models.types import NodeType, Status


def test_types_values():
    assert NodeType.MEMORY.value == "memory"
    assert NodeType.MEMORYLINK.value == "memorylink"
    assert Status.TODO.value == "todo"
