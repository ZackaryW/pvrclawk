from pvrclawk.membank.models.nodes import (
    Bug,
    Feature,
    Issue,
    Memory,
    MemoryLink,
    Pattern,
    Progress,
    Story,
    SubTask,
    Task,
)


def test_memory_node():
    node = Memory(content="hello")
    assert node.content == "hello"


def test_memorylink_node():
    node = MemoryLink(title="TCP", summary="sum", file_path=".pvrclawk/additional_memory/tcp.md")
    assert node.file_path.endswith(".md")


def test_other_node_types():
    story = Story(role="dev", benefit="ship")
    feature = Feature(component="x", test_scenario="Given", expected_result="Then")
    assert story.role == "dev"
    assert feature.component == "x"
    assert story.othermeta == {}
    assert feature.othermeta == {}
    assert Pattern(content="a", pattern_type="arch").pattern_type == "arch"
    assert Progress(content="a").content == "a"


def test_jira_aligned_node_types_have_status_and_othermeta():
    issue = Issue(content="sync jira issue")
    bug = Bug(content="fix bug")
    task = Task(content="implement endpoint")
    subtask = SubTask(content="write tests")

    assert issue.status.value == "todo"
    assert bug.status.value == "todo"
    assert task.status.value == "todo"
    assert subtask.status.value == "todo"
    assert issue.othermeta == {}
    assert bug.othermeta == {}
    assert task.othermeta == {}
    assert subtask.othermeta == {}
