from pvrclawk.app import main


def test_report_mood_updates_value(runner, tmp_path):
    db_path = tmp_path / ".pvrclawk"
    runner.invoke(main, ["membank", "--path", str(db_path), "init"])
    result = runner.invoke(main, ["membank", "--path", str(db_path), "report", "mood", "tcp", "0.2"])
    assert result.exit_code == 0
    assert "tcp" in result.output
