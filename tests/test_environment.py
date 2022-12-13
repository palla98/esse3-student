import os

from esse3_student_cli.primitives import Username, Password
from esse3_student_cli.utils.cred import take_credentials

USERNAME = take_credentials("username")
PASSWORD = take_credentials("password")

#USERNAME = os.environ.get("CLI_STUDENT_USERNAME")
#PASSWORD = os.environ.get("CLI_STUDENT_PASSWORD")


def test_environment():
    assert USERNAME is not None
    assert PASSWORD is not None

    assert Username.parse(USERNAME).value == USERNAME
    assert Password.parse(PASSWORD).value == PASSWORD

