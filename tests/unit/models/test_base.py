from pvrclawk.membank.models.base import BaseNode


def test_base_node_defaults():
    node = BaseNode()
    assert node.uid
    assert node.tags == {}


def test_base_node_add_tag():
    node = BaseNode()
    node.add_tag("tcp", 0.7)
    assert node.tags["tcp"] == 0.7
