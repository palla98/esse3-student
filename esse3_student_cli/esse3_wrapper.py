import dataclasses
import time
from dataclasses import InitVar
from typing import List


import typeguard
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from esse3_student_cli.utils import validators
from esse3_student_cli.primitives import Username, Password, Exam, ExaminationProcedure, ExamNotes
import asyncio

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
        self.maximize()
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
        """WebDriverWait(self.driver, 20).until \
            (EC.visibility_of_element_located(
                (By.XPATH, "//*[@id='esse3']")))"""
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
            (EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/table/tbody/tr[1]/td[5]/div/a")))
        carrier.click()

    def fetch_exams(self) -> List[Exam]:
        self.driver.get(EXAMS_URL)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/div/table")))
        except NoSuchElementException:
            return []

        exams = self.driver.find_elements(By.XPATH, "//*[@id='app-tabella_appelli']/tbody/tr")
        rows = []

        for index, exam in enumerate(exams, start=1):
            xpath_base = "//*[@id='app-tabella_appelli']/tbody/tr"
            if len(exams) == 1:
                xpath_suffix = ""
            else:
                xpath_suffix = f"[{index}]"
            elements = exam.find_elements(By.XPATH, f"{xpath_base}{xpath_suffix}/td")
            name = elements[1].text
            date = elements[2].text
            s = elements[3].get_attribute('innerText')
            signing_up = s[:10] + " - " + s[10:]
            description = elements[4].get_attribute('innerHTML')
            row = f"{name}&{date}&{signing_up}&{description}"
            rows.append(Exam.of(row))

        print(rows)
        return rows

    def fetch_reservations(self) -> list:

        self.driver.get(RESERVATIONS_URL)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//*[@id='textHeader']")))
        except TimeoutError:
            return []

        reservations = self.driver.find_elements(By.XPATH, "//*[@id='boxPrenotazione']")

        rows = []
        index = 2
        for reservation in reservations:
            name = reservation.find_element(By.XPATH,
                                            f"/html/body/div[2]/div/div/main/div[3]/div/div/div/div[{index}]/h2").text
            start = name.find(" [") # per evitare che stampi anche il codice nel nome
            name = name[:start]
            dict = {"Name": name}
            elements = reservation.find_elements(By.XPATH, "./dl/dt")
            for position, element in enumerate(elements, start=1):
                key = element.text
                value = element.find_element(By.XPATH, f"../dd[{position}]").text
                if position == 1:
                    dict["Date"] = key
                elif key != "Riservato per" and key != "Data Prenotazione":
                    dict[key] = value
            rows.append(dict)
            index += 2
        return rows

    def add_reservation(self, names: list) -> str:

        self.driver.get(EXAMS_URL)
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//table/tbody/tr")))
        exams = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
        values = {}
        entro = False
        if not exams:
            return "empty"
        while names:
            name = names.pop()
            entro = False
            for i, exam in enumerate(exams, start=1):
                if exam.find_element(By.XPATH, f"//table/tbody/tr[{i}]/td[2]").text == name:
                    values[1] = name
                    entro = True
                    exam_link = self.driver.find_element(By.XPATH, f"//table/tbody/tr[{i}]/td/div/a")
                    self.driver.execute_script("arguments[0].scrollIntoView();", exam_link)
                    exam_link.send_keys(Keys.ENTER)
                    save_button = self.driver.find_element(By.XPATH, "//*[@id='btnSalva']")
                    self.driver.execute_script("arguments[0].scrollIntoView();", save_button)
                    save_button.send_keys(Keys.ENTER)
                    break
            if not entro:
                values[0] = name
            self.driver.get(EXAMS_URL)
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//table/tbody/tr")))
            exams = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
        return "ok"

    def remove_reservation(self, names: list) -> {}:

        self.driver.get(RESERVATIONS_URL)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//*[@id='textHeader']")))
        except TimeoutError:
            return "empty"
        values = {
            0: [" "],
            1: [" "],
        }
        boxprenotazione = self.driver.find_elements(By.XPATH, "//*[@id='boxPrenotazione']")
        toolbar = self.driver.find_elements(By.XPATH, "//*[@id='toolbarAzioni']")
        if not boxprenotazione:
            return []
        while names:
            reservation = names.pop()
            found = False
            element = None
            for i, name in enumerate(boxprenotazione, start=1):
                value = name.find_element(By.CLASS_NAME, "record-h2").text
                value = value[:value.index(" [")].strip()
                if value == reservation:
                    for j, remove in enumerate(toolbar, start=1):
                        if j == i:
                            try:
                                element = remove.find_element(By.ID, 'btnCancella')
                                found = True
                                break
                            except NoSuchElementException:
                                values[0].append(reservation)
                    if found:
                        break
            if found:
                element.click()
                confirm = self.driver.find_element(By.XPATH, "//*[@id='btnConferma']")
                confirm.click()
                values[1].append(reservation)
                self.driver.get(RESERVATIONS_URL)
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[@id='textHeader']")))
                boxprenotazione = self.driver.find_elements(By.XPATH, "//*[@id='boxPrenotazione']")
                toolbar = self.driver.find_elements(By.XPATH, "//*[@id='toolbarAzioni']")
        values[0].pop(0)
        values[1].pop(0)
        for k, v in list(values.items()):
            if len(v) == 0:
                values.pop(k)
        print(values)
        return values

    def fetch_booklet(self) -> list[Exam]:

        self.driver.get(BOOKLET_URL)

        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/div/table/tbody/tr")))

        arithmetic_average = self.driver.find_element(By.XPATH, "//div[@id='boxMedie']//li[1]").text.split()[4]
        weighted_average = self.driver.find_element(By.XPATH, "//div[@id='boxMedie']//li[2]").text.split()[4]
        sum = 0

        exams = self.driver.find_elements(By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/div/table/tbody/tr")
        rows = []
        for i, exam in enumerate(exams, start=1):
            name = exam.find_element(By.XPATH, f"/html/body/div[2]/div/div/main/div[3]/div/div/div/table/tbody/tr[{i}]/td[1]/a").text
            academic_year = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{i}]/td[2]").text
            cfu = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{i}]/td[3]").text
            state = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{i}]/td[4]/img").get_attribute('aria-label')
            vote_date = exam.find_element(By.XPATH, f"//*[@id='tableLibretto']/tbody/tr[{i}]/td[6]").text

            if state == "Superata":
                sum = sum + int(cfu)

            row = f"{name}&{academic_year}&{cfu}&{state}&{vote_date}"
            rows.append(Exam.of(row))
        rows.append(Exam.of(f"{arithmetic_average}&{weighted_average}&{sum}"))
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
                if start != 3:
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