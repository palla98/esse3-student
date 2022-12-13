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
    assert "Reservations showcase" in result.stdout




