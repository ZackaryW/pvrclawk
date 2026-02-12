from pvrclawk.app import main


def test_root_help_describes_groups(runner):
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "pvrclawk CLI entrypoint." in result.output
    assert "membank" in result.output
    assert "Manage the graph-based membank." in result.output
    assert "skills" in result.output
    assert "Discover, resolve, and update agent skills." in result.output


def test_membank_help_describes_commands(runner):
    result = runner.invoke(main, ["membank", "--help"])
    assert result.exit_code == 0
    assert "Manage the graph-based membank." in result.output
    assert "init" in result.output
    assert "Initialize membank storage files and directories." in result.output
    assert "focus" in result.output
    assert "Retrieve ranked nodes relevant to query tags." in result.output
    assert "prune" in result.output
    assert "Rebalance node storage clusters and rebuild indexes." in result.output


def test_membank_nested_group_help_describes_subcommands(runner):
    node_help = runner.invoke(main, ["membank", "node", "--help"])
    assert node_help.exit_code == 0
    assert "Create, inspect, list, and remove membank nodes." in node_help.output
    assert "add" in node_help.output
    assert "Create a node for the given node type." in node_help.output
    assert "remove-type" in node_help.output
    assert "Remove all nodes of one type (requires --all)." in node_help.output

    link_help = runner.invoke(main, ["membank", "link", "--help"])
    assert link_help.exit_code == 0
    assert "Manage directional links between nodes." in link_help.output
    assert "chain" in link_help.output
    assert "Create sequential links from a list of UIDs." in link_help.output


def test_skills_help_describes_commands(runner):
    result = runner.invoke(main, ["skills", "--help"])
    assert result.exit_code == 0
    assert "Discover, resolve, and update agent skills." in result.output
    assert "list" in result.output
    assert "List discovered skills across configured repositories." in result.output
    assert "resolve" in result.output
    assert "Resolve skills by keyword matches in names and descriptions." in result.output
    assert "update" in result.output
    assert "Update configured skill repositories by pulling git remotes." in result.output
