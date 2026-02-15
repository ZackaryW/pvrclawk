"""Unit tests for forctx scorer."""

from pvrclawk.membank.core.forctx.scorer import score_nodes_forctx
from pvrclawk.membank.models.nodes import Task


def test_scorer_tag_match_ranks_higher_than_content():
    """Tag match contributes more than content match (tag_weight 2.0 > content_weight 1.0)."""
    task_with_both = Task(content="auth flow", uid="t1")
    task_with_both.add_tag("task", 1.0)

    task_content_only = Task(content="auth flow", uid="t2")

    nodes = [task_with_both, task_content_only]
    tag_tokens = ["task"]
    content_phrases = ["auth"]

    ranked = score_nodes_forctx(nodes, tag_tokens, content_phrases, top=10)
    uids = [uid for uid, _ in ranked]
    assert uids[0] == "t1"
    assert uids[1] == "t2"
    assert ranked[0][1] > ranked[1][1]


def test_scorer_content_only():
    """Query with only content phrase scores by content match."""
    node = Task(content="auth flow", uid="n1")
    ranked = score_nodes_forctx([node], [], ["auth"], top=10)
    assert len(ranked) == 1
    assert ranked[0][0] == "n1"
    assert ranked[0][1] == 1.0


def test_scorer_tag_only():
    """Query with only tag scores by tag match."""
    node = Task(content="x", uid="n1")
    node.add_tag("task", 1.0)
    ranked = score_nodes_forctx([node], ["task"], [], top=10)
    assert len(ranked) == 1
    assert ranked[0][0] == "n1"
    assert ranked[0][1] == 2.0


def test_scorer_case_insensitive_content():
    """Content match is case-insensitive."""
    node = Task(content="Auth Flow", uid="n1")
    ranked = score_nodes_forctx([node], [], ["auth"], top=10)
    assert len(ranked) == 1
    assert ranked[0][1] > 0


def test_scorer_top_limits_results():
    """Only top N nodes returned."""
    nodes = [Task(content="a", uid=f"n{i}") for i in range(5)]
    for n in nodes:
        n.add_tag("t", 1.0)
    ranked = score_nodes_forctx(nodes, ["t"], [], top=2)
    assert len(ranked) == 2


def test_scorer_zero_score_excluded():
    """Nodes with no tag or content match have score 0 and are excluded."""
    node = Task(content="unrelated", uid="n1")
    ranked = score_nodes_forctx([node], ["task"], ["auth"], top=10)
    assert len(ranked) == 0
