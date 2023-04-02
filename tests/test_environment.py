import os

from esse3_student.primitives import Username, Password

USERNAME = os.environ.get("CLI_STUDENT_USERNAME")
PASSWORD = os.environ.get("CLI_STUDENT_PASSWORD")


def test_environment():
    assert USERNAME is not None
    assert PASSWORD is not None

    assert Username.parse(USERNAME).value == USERNAME
    assert Password.parse(PASSWORD).value == PASSWORD

