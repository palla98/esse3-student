import dataclasses
import datetime
import enum
import re

import typeguard

from esse3_student_cli.utils.primitives import bounded_string, bounded_integer
from esse3_student_cli.utils.validators import validate_dataclass, validate

from dateutil.relativedelta import relativedelta


@bounded_integer(min_value=1, max_value=10)
class Integer:
    pass


@bounded_string(min_length=3, max_length=30, pattern=r'[A-Za-z0-9]*')
class Username:
    pass


@bounded_string(min_length=5, max_length=100, pattern=r'[^\n]*')
class Password:
    pass


@bounded_string(min_length=3, max_length=255, pattern=r'[A-Z ]+ \[\d+\]')
class Course:
    pass


@bounded_string(min_length=3, max_length=255, pattern=r"[-A-Z a-z 0-9 \.\/:[\]’'&\n]+")
class Exam:
    pass


class ExaminationProcedure(enum.Enum):
    PRESENCE = 'P'
    REMOTE_EXAM_REQUEST = 'RD'


@bounded_string(min_length=1, max_length=255, pattern=r"[A-Za-z0-9ÀÈÉÌÒÙàèéìòù '\":;.,()\[\]\n_-]*")
class ExamNotes:
    pass


@bounded_integer(min_value=1, max_value=5)
class AcademicYear:
    pass


@bounded_integer(min_value=2010, max_value=datetime.datetime.now().year)
class Year:
    pass


@bounded_string(min_length=6, max_length=11, pattern=r"(Superata|Frequenza attribuita d'ufficio)")
class ExamState:
    pass


@bounded_integer(min_value=18, max_value=30)
class Vote:
    pass


@bounded_string(min_length=1, max_length=2, pattern=r'(6|9|12)')
class Cfu:
    pass
