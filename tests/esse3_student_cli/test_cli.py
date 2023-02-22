import pytest
from typer.testing import CliRunner
from esse3_student_cli.cli import app
from tests.esse3_student_cli.utils.mocks import test_server  # noqa: F401; pylint: disable=unused-variable


@pytest.fixture
def runner(test_server):
    return CliRunner()


def test_reservations(runner):
    result = runner.invoke(app, ["reservations"])
    assert result.exit_code == 0
    assert "RESERVATIONS SHOWCASE" in result.stdout


def test_booklet(runner):
    result = runner.invoke(app, ["booklet"])
    assert result.exit_code == 0
    assert "─────────────────────────────────── Booklet ────────────────────────────────────" in result.stdout
    assert "                                                                              \n" in result.stdout
    assert "  #    Name             Academic Year   CFU   State             Vote            \n" in result.stdout
    assert "────────────────────────────────────────────────────────────────────────────── \n" in result.stdout