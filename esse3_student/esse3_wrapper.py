import dataclasses
import time
import subprocess

import screeninfo
from dataclasses import InitVar
from typing import List, Tuple, Union, Any

import typeguard
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from esse3_student.utils import validators
from esse3_student.primitives import Username, Password, ExamName, Description, Date, SigningUp, \
    AcademicYear, Cfu, ExamStatus, BookletGrade, TaxeID, Amount, TaxeStatus

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


def prompt_position() -> None:

    result = subprocess.run(["xdotool", "getactivewindow"], capture_output=True)
    window_id = result.stdout.decode().strip()
    screen_height = subprocess.check_output(["xdotool", "getdisplaygeometry"]).decode().split()[1]

    subprocess.run(["xdotool", "windowmove", window_id, "0", str(int(screen_height) // 4)])
    subprocess.run(["xdotool", "windowsize", window_id, "50%", "-1"])
    # con -1 l'altezza rimane invariata altrimenti lasciare  str(int(screen_height) // 2)


def driver_position(driver) -> None:

    #self.driver.maximize_window()
    screen = screeninfo.get_monitors()[0]
    width, height = screen.width, screen.height
    driver.set_window_size(width // 2, height)
    driver.set_window_position(width // 2, 0)


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

        self.__login(username, password)

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
            prompt_position()
        driver = webdriver.Chrome(options=options)
        driver_position(driver)

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

        """try:
            WebDriverWait(self.driver, 2).until \
                (EC.visibility_of_element_located(
                    (By.XPATH, "//*[@id='c-s-bn']")))
            self.driver.find_element(By.XPATH, "//*[@id='c-s-bn']").click()
        except:
            pass"""

        try:
            self.driver.find_element(By.ID, 'u').send_keys(username.value)
            self.driver.find_element(By.ID, 'p').send_keys(password.value)
            self.driver.find_element(By.ID, 'btnLogin').send_keys(Keys.RETURN)
            carrier = WebDriverWait(self.driver, 2).until(EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/table/tbody/tr[1]/td[5]/div/a")))
            carrier.click()
        except Exception:
            raise RuntimeError("Wrong credentials")

    def __logout(self) -> None:
        self.driver.get(LOGOUT_URL)

    def minimize(self) -> None:
        self.driver.minimize_window()

    def fetch_exams(self) -> list[tuple[ExamName, Date, SigningUp, Description]]:

        self.driver.get(EXAMS_URL)
        try:
            exams = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_all_elements_located((By.XPATH,
                        "//*[@id='app-tabella_appelli']/tbody/tr")))
        except TimeoutException:
            return []

        rows = []

        for exam in exams:
            elements = exam.find_elements(By.TAG_NAME, "td")
            name = ExamName.of(elements[1].text)
            date = Date.of(elements[2].text)
            signing_up = SigningUp.of(elements[3].get_attribute('innerText').replace("\n", " - "))
            description = Description.of(elements[4].get_attribute("innerHTML"))

            rows.append((name, date, signing_up, description))

        return rows

    def fetch_reservations(self) -> list:

        self.driver.get(RESERVATIONS_URL)
        try:
            reservations = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//*[@id='boxPrenotazione']")))
        except:
            return []

        rows = []

        index = 2
        for reservation in reservations:
            name = reservation.find_element(By.XPATH,
                                            f"/html/body/div[2]/div/div/main/div[3]/div/div/div/div[{index}]/h2").text
            start = name.find(" [")
            name = name[:start]
            dict = {"Name": name}
            elements = reservation.find_elements(By.XPATH, "./dl/dt")
            for position, element in enumerate(elements, start=1):
                key = element.text
                value = element.find_element(By.XPATH, f"../dd[{position}]").text
                if position == 1:
                    dict["Date"] = key
                elif key != "Riservato per" and key != "Data Prenotazione" and key != '':
                    dict[key] = value
            rows.append(dict)
            index += 2

        return rows

    def add(self, names: list[ExamName]) -> tuple[list[ExamName], int]:

        self.driver.get(EXAMS_URL)
        click = 7
        try:
            exams = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//table/tbody/tr")))
        except:
            return [], click

        added = []

        while names:
            name = names.pop().value
            wrong = True
            for i, exam in enumerate(exams, start=1):
                exam_name = name.upper()
                if exam.find_element(By.XPATH, f"//table/tbody/tr[{i}]/td[2]").text == exam_name:
                    added.append(ExamName.of(f"{exam_name}"))
                    wrong = False
                    exam_link = self.driver.find_element(By.XPATH, f"//table/tbody/tr[{i}]/td/div/a")
                    self.driver.execute_script("arguments[0].scrollIntoView();", exam_link)
                    exam_link.send_keys(Keys.ENTER)
                    save_button = self.driver.find_element(By.XPATH, "//*[@id='btnSalva']")
                    self.driver.execute_script("arguments[0].scrollIntoView();", save_button)
                    save_button.send_keys(Keys.ENTER)
                    click += 2
                    break

            if len(names) != 0:
                self.driver.get(EXAMS_URL)
                if not wrong:
                    click += 1
                exams = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_all_elements_located((By.XPATH, "//table/tbody/tr")))

        return added, click

    def remove(self, names: list[ExamName]) -> tuple[{}, int]:

        self.driver.get(RESERVATIONS_URL)
        click = 7

        try:
            box_prenotazione = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//*[@id='boxPrenotazione']")))
            tool_bar = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//*[@id='toolbarAzioni']")))
        except:
            return {}, click

        values = {
            0: [],
            1: [],
        }

        for reservation in names:
            found = False
            for i, name in enumerate(box_prenotazione, start=1):
                value = name.find_element(By.CLASS_NAME, "record-h2").text.split(" [")[0].strip()
                reservation_name = reservation.value.upper()
                if value == reservation_name:
                    try:
                        element = tool_bar[i - 1].find_element(By.ID, 'btnCancella')
                        element.click()
                        confirm = self.driver.find_element(By.XPATH, "//*[@id='btnConferma']")
                        confirm.click()
                        click += 2
                        values[1].append(reservation_name)
                        found = True
                        break
                    except NoSuchElementException:
                        pass
            if not found:
                values[0].append(reservation.value)
            else:
                self.driver.get(RESERVATIONS_URL)
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[@id='textHeader']")))
                box_prenotazione = self.driver.find_elements(By.XPATH, "//*[@id='boxPrenotazione']")
                tool_bar = self.driver.find_elements(By.XPATH, "//*[@id='toolbarAzioni']")

        values = {k: v for k, v in values.items() if v}

        return values, click

    def fetch_booklet(self) -> tuple[list[tuple[ExamName, AcademicYear, Cfu, ExamStatus, BookletGrade, Date]], tuple[float, int]]:

        self.driver.get(BOOKLET_URL)

        exams = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/div/table/tbody/tr")))

        weighted_average = self.driver.find_element(By.XPATH, "//div[@id='boxMedie']//li[2]").text.split()[4]
        cfu_achieved = 0

        rows = []

        for i, exam in enumerate(exams, start=1):

            name = exam.find_element(By.XPATH, f"/html/body/div[2]/div/div/main/div[3]/div/div/div/table/tbody/tr[{i}]/td[1]/a").text
            academic_year = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{i}]/td[2]").get_attribute("innerHTML")
            cfu = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{i}]/td[3]").get_attribute("innerHTML")
            status = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{i}]/td[4]/img").get_attribute('aria-label')
            grade_date = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{i}]/td[6]").get_attribute("innerHTML")

            # Remove characters preceding the first space immediately after the hyphen.
            name = name[name.index(" - ") + 3:]
            # Separate the string "grade_date" into two parts using the separator " - "
            grade, date = (grade_date.replace("&nbsp;-&nbsp;", " - ").split(" - ") + [''])[:2]

            grade = "ELIGIBLE" if grade == "IDO" else grade or "..."
            date = Date.of(date or "None")

            if status == "Superata":
                status = "Passed"
                cfu_achieved += int(cfu)
            else:
                status = "Ex officio assigned frequency"

            rows.append((ExamName.of(name), AcademicYear.of(int(academic_year)), Cfu.of(cfu),
                         ExamStatus.of(status), BookletGrade.of(grade), date))

        statistics = (float(weighted_average), int(cfu_achieved))

        return rows, statistics


    def fetch_taxes(self) -> tuple[list[tuple[TaxeID, Date, Amount, TaxeStatus]], int]:

        self.driver.get(TAXES_URL)
        click = 7

        taxes = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//*[@id='tasse-tableFatt']/tfoot/tr/td/div/ul/li/a")))
        rows = []

        start = 3
        while start < len(taxes):
            page = self.driver.find_element(By.XPATH, f"//*[@id='tasse-tableFatt']/tfoot/tr/td/div/ul/li[{start}]/a")
            if 0 < int(page.text) < 10:
                if start != 3:
                    page.click()
                    click += 1
                time.sleep(1)
                taxes = self.driver.find_elements(By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/table[1]/tbody/tr")
                for index, taxe in enumerate(taxes, start=1):

                    id = taxe.find_element(By.XPATH, f"/html/body/div[2]/div/div/main/div[3]/div/div/table[1]/tbody/tr[{index}]/td[1]/a").text
                    expiration_date = taxe.find_element(By.XPATH, f"/html/body/div[2]/div/div/main/div[3]/div/div/table[1]/tbody/tr[{index}]/td[4]").get_attribute('data-sort-value')
                    amount = taxe.find_element(By.XPATH, f"/html/body/div[2]/div/div/main/div[3]/div/div/table[1]/tbody/tr[{index}]/td[5]").text
                    payment_status = taxe.find_element(By.XPATH, f"/html/body/div[2]/div/div/main/div[3]/div/div/table[1]/tbody/tr[{index}]/td[6]").text

                    if expiration_date is not None:
                        year, month, day = expiration_date.split("-")
                        expiration_date = f"{day}/{month}/{year}"

                    rows.append((TaxeID.of(id), Date.of(expiration_date or "None"), Amount.of(amount), TaxeStatus.of(payment_status)))
            start = start + 1

        return rows, click
