from pathlib import Path

from pvrclawk.membank.core.storage.engine import StorageEngine
from pvrclawk.membank.models.link import Link


def test_update_link_weight_by_tags(tmp_path: Path):
    storage = StorageEngine(tmp_path / ".pvrclawk")
    storage.init_db()
    storage.save_link(Link(source="a", target="b", tags=["tcp", "method"], weight=1.0))
    updated = storage.adjust_link_weights_by_tags(["tcp", "method"], 0.1)
    assert updated == 1
    links = storage.load_links(["a"])
    assert links[0].weight == 1.1
