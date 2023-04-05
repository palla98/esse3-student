from esse3_student.primitives import ExamName, Date, Username, TaxeID, TaxeStatus, Grade


def test_exam_name_of():
    assert ExamName.of("TRAINING").value == "TRAINING"


def test_date_of():
    assert Date.of("20/04/2022").value == "20/04/2022"


def test_username_of():
    assert Username.of("pllnts99d20m208d").value == "pllnts99d20m208d"


def test_taxe_id_of():
    assert TaxeID.of("1453765").value == "1453765"


def test_taxe_status_of():
    assert TaxeStatus.of(" pagato").value == " pagato"


def test_grade_of():
    assert Grade.of("30").value == 30