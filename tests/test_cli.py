from typer.testing import CliRunner

from research_graph.cli import app

runner = CliRunner()


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_check_config_command() -> None:
    result = runner.invoke(app, ["check-config"])

    assert result.exit_code == 0
    assert "Configuration is valid." in result.stdout
    assert "GitHub token configured: no" in result.stdout


def test_check_config_does_not_reveal_token(
    monkeypatch,
) -> None:
    monkeypatch.setenv("RG_GITHUB_TOKEN", "secret-test-token")

    result = runner.invoke(app, ["check-config"])

    assert result.exit_code == 0
    assert "secret-test-token" not in result.stdout
    assert "GitHub token configured: yes" in result.stdout
