import datetime

from esse3_student.utils.primitives import bounded_string, bounded_integer


@bounded_string(min_length=3, max_length=30, pattern=r'[A-Za-z0-9]*')
class Username:
    pass


@bounded_string(min_length=5, max_length=100, pattern=r'[^\n]*')
class Password:
    pass


@bounded_string(min_length=3, max_length=50, pattern=r"[A-Z a-z ’']+")
class ExamName:
    pass


@bounded_string(min_length=3, max_length=255, pattern=r"[-A-Z a-z 0-9 \.\/:[\]’'&\n]+")
class Description:
    pass


@bounded_string(min_length=4, max_length=10, pattern=r"^(?:(?:0?[1-9]|[12]\d|3[01])\/(?:0?[1-9]|1[0-2])\/(?:19|20)\d{2}|None)$")
class Date:
    pass


@bounded_string(min_length=23, max_length=23, pattern=r"^(?:(?:0?[1-9]|[12]\d|3[01])\/(?:0?[1-9]|1[0-2])\/(?:19|20)\d{2})\s*-\s*(?:(?:0?[1-9]|[12]\d|3[01])\/(?:0?[1-9]|1[0-2])\/(?:19|20)\d{2})$")
class SigningUp:
    pass


@bounded_string(min_length=7, max_length=7, pattern=r"[0-9]+")
class TaxeID:
    pass


@bounded_string(min_length=7, max_length=18, pattern=r"( pagato| non pagato| pagato confermato)")
class TaxeStatus:
    pass


@bounded_string(min_length=6, max_length=9, pattern=r"^-?\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s€$")
class Amount:
    pass


@bounded_integer(min_value=1, max_value=3)
class AcademicYear:
    pass


@bounded_integer(min_value=2010, max_value=datetime.datetime.now().year)
class Year:
    pass


@bounded_string(min_length=6, max_length=29, pattern=r"(Passed|Ex officio assigned frequency)")
class ExamStatus:
    pass


@bounded_integer(min_value=18, max_value=30)
class Grade:
    pass


@bounded_string(min_length=2, max_length=8, pattern=r"(ELIGIBLE|1[89]|[2-2][0-9]|30|...)")
class BookletGrade:
    pass


@bounded_string(min_length=1, max_length=2, pattern=r'(3|6|9|12|24)')
class Cfu:
    pass


