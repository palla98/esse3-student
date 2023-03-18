import pytest

from esse3_student_cli.esse3_wrapper import Esse3Wrapper
from esse3_student_cli.primitives import ExamName
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


def test_exams(esse3_wrapper):

    exams = esse3_wrapper.fetch_exams()
    assert len(exams) == 4
    name = exams[0][0].value
    assert name == "BUSINESS GAME"


def test_empty_exams(esse3_wrapper):

    exams = esse3_wrapper.fetch_exams()
    assert len(exams) == 0


def test_fetch_reservations(esse3_wrapper):
    reservations = esse3_wrapper.fetch_reservations()
    assert len(reservations) == 2
    name = reservations[0]["Name"]
    assert  name == "PROCESS MINING"


def test_fetch_empty_reservations(esse3_wrapper):
    reservations = esse3_wrapper.fetch_reservations()
    assert len(reservations) == 0


def test_remove_reservations(esse3_wrapper):
    reservations = [ExamName("TRAINING")]
    values, click = esse3_wrapper.remove(reservations)
    print(values)
    first_value = " ".join([x for x in values[0]])
    assert first_value == "TRAINING"
    assert click == 7


def test_add_exams_but_empty(esse3_wrapper):
    n1 = ExamName("DATA ANALYTICS")
    n2 = ExamName("TRAINING")
    lista = [n1, n2]

    added, click = esse3_wrapper.add(lista)
    assert len(added) == 0
    assert click == 7


"""def test_add_exams_confirm(esse3_wrapper):
    n1 = Name("DATA ANALYTICS")
    lista = [n1]

    added, click = esse3_wrapper.add(lista)
    assert len(added) == 1"""


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

def test_fetch_booklet(esse3_wrapper):
    exams, statistics = esse3_wrapper.fetch_booklet()
    assert len(exams) == 15
    name = exams[2][0].value
    assert name == "CRYPTOGRAPHY"


def test_fetch_first_page_taxes(esse3_wrapper):
    taxes, click = esse3_wrapper.fetch_taxes()

    assert len(taxes) == 10
