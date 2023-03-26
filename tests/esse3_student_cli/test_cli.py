import pytest
from typer.testing import CliRunner
from esse3_student_cli.cli import app
from tests.esse3_student_cli.utils.mocks import test_server  # noqa: F401; pylint: disable=unused-variable


@pytest.fixture
def runner(test_server):
    return CliRunner()


def test_exams(runner):
    result = runner.invoke(app, ["exams"])
    assert result.exit_code == 0
    assert "EXAMS SHOWCASE" in result.stdout
    assert "  2     DATA ANALYTICS     06/02/2023     " in result.stdout


def test_exams_empty(runner):
    result = runner.invoke(app, ["exams"])
    assert result.exit_code == 0
    assert "No exams available!!!" in result.stdout


def test_reservations(runner):
    result = runner.invoke(app, ["reservations"])
    assert result.exit_code == 0
    assert "RESERVATIONS SHOWCASE" in result.stdout


def test_reservations_empty(runner):
    result = runner.invoke(app, ["reservations"])
    assert result.exit_code == 0
    assert "No exams booked!!!" in result.stdout


def test_add_no_exam_available(runner):
    result = runner.invoke(app, ["add", "TRAINING"])
    assert result.exit_code == 0
    assert "No exams available or wrong names passed!!!" in result.stdout


def test_add_incorrect_names(runner):
    result = runner.invoke(app, ["add", "*"])
    assert result.exit_code == 0
    assert "Invalid strings" in result.stdout


def test_remove_no_exam_available(runner):
    result = runner.invoke(app, ["remove", "TRAINING"])
    assert result.exit_code == 0
    assert "❌ No exams to remove or wrong values passed!!!" in result.stdout


def test_remove_incorrect_names(runner):
    result = runner.invoke(app, ["remove", "*"])
    assert result.exit_code == 0
    assert "Invalid strings" in result.stdout


def test_remove(runner):
    result = runner.invoke(app, ["remove", "TRAINING"])
    assert result.exit_code == 0
    assert "❌ Impossible to remove: TRAINING cause subscription" in result.stdout


def test_booklet(runner):
    result = runner.invoke(app, ["booklet"])
    assert result.exit_code == 0
    assert "BOOKLET SHOWCASE" in result.stdout


def test_taxes(runner):
    result = runner.invoke(app, ["taxes"])
    assert result.exit_code == 0
    assert "TAXES SHOWCASE" in result.stdout