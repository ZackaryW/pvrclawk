from pvrclawk.membank.models.link import Link


def test_link_defaults():
    link = Link(source="a", target="b")
    assert link.uid
    assert link.weight == 1.0
    assert link.decay == 1.0
