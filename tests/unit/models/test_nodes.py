from pvrclawk.membank.models.nodes import (
    Active,
    Archive,
    Feature,
    Memory,
    MemoryLink,
    Pattern,
    Progress,
    Story,
)


def test_memory_node():
    node = Memory(content="hello")
    assert node.content == "hello"


def test_memorylink_node():
    node = MemoryLink(title="TCP", summary="sum", file_path=".pvrclawk/additional_memory/tcp.md")
    assert node.file_path.endswith(".md")


def test_other_node_types():
    assert Story(role="dev", benefit="ship").role == "dev"
    assert Feature(component="x", test_scenario="Given", expected_result="Then").component == "x"
    assert Active(content="a", focus_area="b").focus_area == "b"
    assert Archive(content="a", archived_from="active").archived_from == "active"
    assert Pattern(content="a", pattern_type="arch").pattern_type == "arch"
    assert Progress(content="a").content == "a"
