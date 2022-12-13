import dataclasses
import time
from dataclasses import InitVar
from typing import List

import typeguard
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from esse3_student_cli.utils import validators
from esse3_student_cli.primitives import Username, Password, Exam, ExaminationProcedure, ExamNotes

ESSE3_SERVER = "https://unical.esse3.cineca.it"
LOGIN_URL = f'{ESSE3_SERVER}/auth/Logon.do?menu_opened_cod='
LOGOUT_URL = f'{ESSE3_SERVER}/Logout.do?menu_opened_cod='
EXAMS_URL = f'{ESSE3_SERVER}/auth/studente/Appelli/AppelliF.do?menu_opened_cod=menu_link-navbox_studenti_Esami'
RESERVATIONS_URL = f'{ESSE3_SERVER}/auth/studente/Appelli/BachecaPrenotazioni.do?menu_opened_cod=menu_link-navbox_studenti_Esami'
BOOKLET_URL = f'{ESSE3_SERVER}/auth/studente/Libretto/LibrettoHome.do?menu_opened_cod=menu_link-navbox_studenti_Carriera'
TAXES_URL = f'{ESSE3_SERVER}/auth/studente/Tasse/ListaFatture.do?menu_opened_cod=menu_link-navbox_studenti_Segreteria'


def change_esse3_server(url):
    global ESSE3_SERVER, LOGIN_URL, LOGOUT_URL, EXAMS_URL, RESERVATIONS_URL, BOOKLET_URL, TAXES_URL

    LOGIN_URL = LOGIN_URL.replace(ESSE3_SERVER, url, 1)
    LOGOUT_URL = LOGOUT_URL.replace(ESSE3_SERVER, url, 1)
    EXAMS_URL = EXAMS_URL.replace(ESSE3_SERVER, url, 1)
    RESERVATIONS_URL = RESERVATIONS_URL.replace(ESSE3_SERVER, url, 1)
    BOOKLET_URL = BOOKLET_URL.replace(ESSE3_SERVER, url, 1)
    TAXES_URL = TAXES_URL.replace(ESSE3_SERVER, url, 1)

    ESSE3_SERVER = url


@typeguard.typechecked
@dataclasses.dataclass(frozen=True)
class Esse3Wrapper:
    key: InitVar[object]
    username: InitVar[Username]
    password: InitVar[Password]
    debug: bool = dataclasses.field(default=False)
    driver: webdriver.Chrome = dataclasses.field(default_factory=webdriver.Chrome)
    __key = object()

    def __post_init__(self, key: object, username: Username, password: Password):
        validators.validate_dataclass(self)
        validators.validate('key', key, equals=self.__key, help_msg="Can only be instantiated using a factory method")
        # self.maximize()
        self.__login(username, password)
        self.choose_carrier()  # commentare quando si fanno i test

    def __del__(self):
        if not self.debug:
            try:
                self.__logout()
                self.driver.close()
            except WebDriverException:
                pass
            except ValueError:
                pass

    @classmethod
    def create(cls, username: str, password: str, debug: bool = False, detached: bool = False,
               headless: bool = True) -> 'Esse3Wrapper':
        options = webdriver.ChromeOptions()
        options.headless = headless
        if debug or detached:
            options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options)

        return Esse3Wrapper(
            key=cls.__key,
            username=Username.parse(username),
            password=Password.parse(password),
            debug=debug,
            driver=driver,
        )

    @property
    def is_headless(self) -> bool:
        return self.driver.execute_script("return navigator.webdriver")

    def __login(self, username: Username, password: Password) -> None:
        self.driver.get(LOGIN_URL)
        self.driver.find_element(By.ID, 'u').send_keys(username.value)
        self.driver.find_element(By.ID, 'p').send_keys(password.value)
        self.driver.find_element(By.ID, 'btnLogin').send_keys(Keys.RETURN)

    def __logout(self) -> None:
        self.driver.get(LOGOUT_URL)

    def minimize(self) -> None:
        self.driver.minimize_window()

    def maximize(self) -> None:
        self.driver.maximize_window()

    def choose_carrier(self) -> None:
        # nota: dentro la funzione visibility_of_element_located i due argomenti devono essere passati nelle () per essere come unico arg
        carrier = WebDriverWait(self.driver, 10).until\
            (EC.visibility_of_element_located((By.ID, "gu_link_sceltacarriera_218558")))
        carrier.click()

    def fetch_exams(self) -> List[Exam]:
        self.driver.get(EXAMS_URL)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//*[@id='app-tabella_appelli']/tbody/tr")))
        except:
            return list()

        exams = self.driver.find_elements(By.XPATH, "//*[@id='app-tabella_appelli']/tbody/tr")

        rows = []

        for index, exam in enumerate(exams):
            if len(exams) == 1:
                name = exam.find_element(By.XPATH, "//*[@id='app-tabella_appelli']/tbody/tr/td[2]")
                date = exam.find_element(By.XPATH, "//*[@id='app-tabella_appelli']/tbody/tr/td[3]")
            else:
                name = exam.find_element(By.XPATH, f"f//*[@id='app-tabella_appelli']/tbody/tr[{index}]/td[2]")
                date = exam.find_element(By.XPATH, f"f//*[@id='app-tabella_appelli']/tbody/tr[{index}]/td[3]")
            row = name.text + " " + date.text
            rows.append(Exam.of(row))
        return rows

    def fetch_reservations(self) -> List[Exam]:

        self.driver.get(RESERVATIONS_URL)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//*[@id='boxPrenotazione']")))
        except:
            return list()

        reservations = self.driver.find_elements(By.XPATH,
                                            "//*[@id='boxPrenotazione']")

        rows = []
        for index, reservation in enumerate(reservations):
            name = reservation.find_element(By.XPATH, "//*[@id='boxPrenotazione']/h2")
            date = reservation.find_element(By.XPATH, "//*[@id='boxPrenotazione']/dl/dt[1]")
            reservation_number = reservation.find_element(By.XPATH, "//*[@id='boxPrenotazione']/dl/dd[3]")
            exam_type = reservation.find_element(By.XPATH, "//*[@id='boxPrenotazione']/dl/dd[4]")
            examination_procedure = reservation.find_element(By.XPATH, "//*[@id='boxPrenotazione']/dl/dd[5]")
            reservation_date = reservation.find_element(By.XPATH, "//*[@id='boxPrenotazione']/dl/dd[8]")
            professor = reservation.find_element(By.XPATH, "//*[@id='boxPrenotazione']/dl/dd[10]")

            row = name.text + "&" + date.text  + "&" + reservation_number.text +\
                    "&" + exam_type.text + "&" + examination_procedure.text + "&" + reservation_date.text + "&" +\
                    professor.text
            rows.append(Exam.of(row))
        return rows

    def add_reservation(self, index: int, examination_procedure: ExaminationProcedure, note: ExamNotes) -> None:

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/div/table/tbody/tr")))

        if index == 1:
            self.driver.find_element(By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/div/table/tbody/tr/td[1]/div/a").click()
        else:
            self.driver.find_element(By.XPATH, f"/html/body/div[2]/div/div/main/div[3]/div/div/div/table/tbody/tr[{index}/td[1]/div/a").click()

        # solo in debug mode funziona il blocco sottostante
        """
        if examination_procedure.value == "O":
            self.driver.find_element(By.XPATH, "//*[@id='app-selectionSvolgEsame']").send_keys("RD")
        else:
            self.driver.find_element(By.XPATH, "//*[@id='app-selectionSvolgEsame']").send_keys("P")
        """
        self.driver.find_element(By.XPATH, "//*[@id='app-textAreaNoteDoc']").send_keys(note.value)
        WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='btnSalva']"))).click()

    def remove_reservation(self, index: int) -> None:

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/div/div[2]")))
        remove = self.driver.find_element(By.XPATH,
                                            f"/html/body/div[2]/div/div/main/div[3]/div/div/div/div[{1+2*index}]/a[1]")
        remove.click()
        confirm = self.driver.find_element(By.XPATH, "//*[@id='btnConferma']")
        confirm.click()

    def fetch_booklet(self) -> List[Exam]:

        self.driver.get(BOOKLET_URL)
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/div/table/tbody/tr")))
        exams = self.driver.find_elements(By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/div/table/tbody/tr")
        rows = []
        for index, exam in enumerate(exams, start=1):
            name = exam.find_element(By.XPATH, f"/html/body/div[2]/div/div/main/div[3]/div/div/div/table/tbody/tr[{index}]/td[1]/a")
            academic_year = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{index}]/td[2]")
            cfu = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{index}]/td[3]")
            state = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{index}]/td[4]/img")
            vote_date = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{index}]/td[6]")

            row = name.text + "&" + academic_year.text + "&" + cfu.text + \
                  "&" + state.get_attribute('aria-label') + "&" + vote_date.text
            rows.append(Exam.of(row))

        return rows

    def fetch_exams_average(self) -> str:

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='voce-sel']")))
        arithmetic_average = self.driver.find_element(By.XPATH, "//div[@id='boxMedie']//li[1]")
        weighted_average = self.driver.find_element(By.XPATH, "//div[@id='boxMedie']//li[2]")

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/div/table/tbody/tr")))
        exams = self.driver.find_elements(By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/div/table/tbody/tr")
        sum = 0
        for index, exam in enumerate(exams, start=1):
            cfu = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{index}]/td[3]")
            state = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{index}]/td[4]/img")

            if state.get_attribute('aria-label') == "Superata":
                sum = sum + int(cfu.text)

        row = arithmetic_average.text + "&" + weighted_average.text + "&" + str(sum)

        return row

    def fetch_taxes(self) -> List[str]:  # la cosa giusta da fare è ritornare una tupla di primitive di domineo anche se ha poco senso

        self.driver.get(TAXES_URL)

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='tasse-tableFatt']/tfoot/tr/td/div/ul")))
        taxes = self.driver.find_elements(By.XPATH, "//*[@id='tasse-tableFatt']/tfoot/tr/td/div/ul/li/a")

        rows = []

        start = 3
        while start < len(taxes):
            page = self.driver.find_element(By.XPATH, f"//*[@id='tasse-tableFatt']/tfoot/tr/td/div/ul/li[{start}]/a")
            if 0 < int(page.text) < 10:
                page.click()
                time.sleep(1)
                taxes = self.driver.find_elements(By.XPATH,
                                                  "/html/body/div[2]/div/div/main/div[3]/div/div/table[1]/tbody/tr")
                for index, taxe in enumerate(taxes, start=1):
                    id = taxe.find_element(By.XPATH,
                                           f"/html/body/div[2]/div/div/main/div[3]/div/div/table[1]/tbody/tr[{index}]/td[1]/a")
                    expiration_date = taxe.find_element(By.XPATH,
                                                        f"/html/body/div[2]/div/div/main/div[3]/div/div/table[1]/tbody/tr[{index}]/td[5]")
                    amount = taxe.find_element(By.XPATH,
                                               f"/html/body/div[2]/div/div/main/div[3]/div/div/table[1]/tbody/tr[{index}]/td[6]")
                    payment_status = taxe.find_element(By.XPATH,
                                                       f"/html/body/div[2]/div/div/main/div[3]/div/div/table[1]/tbody/tr[{index}]/td[7]")

                    row = id.text + "&" + str(expiration_date.get_dom_attribute('data-sort-value')) + "&" + amount.text + "&" + payment_status.text
                    rows.append(row)
            start = start + 1

        return rows