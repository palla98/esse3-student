import pytest

from esse3_student_cli.esse3_wrapper import Esse3Wrapper
from tests.test_environment import USERNAME, PASSWORD
from tests.esse3_student_cli.utils.mocks import test_server  # noqa: F401 # pylint:disable=unused-import


@pytest.fixture
def esse3_wrapper(test_server):
    return Esse3Wrapper.create(
        username=USERNAME,
        password=PASSWORD,
        debug=True,
        detached=False,
    )


def test_fetch_reservations(esse3_wrapper):
    exams = esse3_wrapper.fetch_reservations()
    assert len(exams) == 1


def test_fetch_taxes_first_page(esse3_wrapper):
    taxes = esse3_wrapper.fetch_taxes()
    assert len(taxes) == 10
    assert taxes[0] == "2013675&2022-12-22&16,50 €& non pagato"
'''

def test_fetch_exams(esse3_wrapper):
    courses = esse3_wrapper.fetch_courses()
    assert courses
    exams = esse3_wrapper.fetch_exams(courses[0])
    assert len(exams) == 2
'''





