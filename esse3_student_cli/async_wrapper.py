import dataclasses
import time
from dataclasses import InitVar
from typing import List

from asyncselenium.webdriver.remote.async_webdriver import AsyncWebdriver
from asyncselenium.webdriver.support.async_wait import AsyncWebDriverWait
from asyncselenium.webdriver.support import async_expected_conditions as ec

import typeguard
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys
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
    driver: AsyncWebdriver = dataclasses.field(default_factory=AsyncWebdriver)
    __key = object()

    async def __post_init__(self, key: object, username: Username, password: Password):
        validators.validate_dataclass(self)
        validators.validate('key', key, equals=self.__key, help_msg="Can only be instantiated using a factory method")
        await self.maximize()
        await self.__login(username, password)
        await self.choose_carrier()  # commentare quando si fanno i test

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
    async def create(cls, username: str, password: str, debug: bool = False, detached: bool = False,
                     headless: bool = True) -> 'Esse3Wrapper':
        options = webdriver.ChromeOptions()
        options.headless = headless
        if debug or detached:
            options.add_experimental_option("detach", True)
        driver = await AsyncWebdriver(options=options)

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

    async def __login(self, username: Username, password: Password) -> None:
        await self.driver.get(LOGIN_URL)
        await self.driver.find_element(By.ID, 'u').send_keys(username.value)
        await self.driver.find_element(By.ID, 'p').send_keys(password.value)
        await self.driver.find_element(By.ID, 'btnLogin').send_keys(Keys.RETURN)

    async def __logout(self) -> None:
        await self.driver.aget(LOGOUT_URL)

    async def minimize(self) -> None:
        await self.driver.aminimize_window()

    async def maximize(self) -> None:
        await self.driver.amaximize_window()

    async def choose_carrier(self) -> None:
        carrier = await asyncio.wait_for(
            self.driver.find_element(By.XPATH,
                                     "/html/body/div[2]/div/div/main/div[3]/div/div/table/tbody/tr[1]/td[5]/div/a"),
            timeout=10
        )
        await carrier.click()

    async def fetch_exams(self) -> List[Exam]:
        await self.driver.get(EXAMS_URL)
        try:
            await asyncio.wait_for(
                EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/div/table")),
                timeout=10)
        except:
            return list()

        exams = await self.driver.find_elements(By.XPATH, "//*[@id='app-tabella_appelli']/tbody/tr")
        rows = []

        for index, exam in enumerate(exams, start=1):
            xpath_base = "//*[@id='app-tabella_appelli']/tbody/tr"
            if len(exams) == 1:
                xpath_suffix = ""
            else:
                xpath_suffix = f"[{index}]"
            elements = await exam.find_elements(By.XPATH, f"{xpath_base}{xpath_suffix}/td")
            if self.debug:
                name, date, signing_up, description = [await e.text for e in elements[1:5]]
                row = f"{name}&{date}&{signing_up}&{description}"
            else:
                name, date = [await e.text for e in elements[1:3]]
                row = f"{name}&{date}"
            rows.append(Exam.of(row))
        return rows

    def fetch_reservations(self) -> List:

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
            start = name.find("[") # per evitare che stampi anche il codice nel nome
            name = name[:start]
            dict = {"Name": name}
            elements = reservation.find_elements(By.XPATH, "./dl/dt")
            for position, element in enumerate(elements, start=1):
                key = element.text
                value = element.find_element(By.XPATH, f"../dd[{position}]").text
                if position == 1:
                    dict["Date"] = key
                else:
                    dict[key] = value
            rows.append(dict)
            index += 2
        return rows
    '''
    rows = []
    index = 2
    for reservation in reservations:
        name = reservation.find_element(By.XPATH, f"/html/body/div[2]/div/div/main/div[3]/div/div/div/div[{index}]/h2")
        dict = {
            "Name": name.text,
        }
        elements = self.driver.find_elements(By.XPATH,
                                             f"/html/body/div[2]/div/div/main/div[3]/div/div/div/div[{index}]/dl/dt")
        for position, element in enumerate(elements, start=1):
            key = element.find_element(By.XPATH,
                                       f"/html/body/div[2]/div/div/main/div[3]/div/div/div/div[{index}]/dl/dt[{position}]")
            value = element.find_element(By.XPATH,
                                         f"/html/body/div[2]/div/div/main/div[3]/div/div/div/div[{index}]/dl/dd[{position}]")
            if position == 1:
                dict["Date"] = key.text
            else:
                dict[key.text] = value.text
            position += 1

        rows.append(dict)
        index += 2
    '''

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

    def remove_reservation(self, reservation: str) -> str:

        self.driver.get(RESERVATIONS_URL)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div/main/div[3]/div/div/div/div[2]")))
            boxprenotazione = self.driver.find_elements(By.XPATH, "//*[@id='boxPrenotazione']")
            toolbar = self.driver.find_elements(By.XPATH, "//*[@id='toolbarAzioni']")
            found = False
            for i, name in enumerate(boxprenotazione, start=1):
                if name.find_element(By.CLASS_NAME, "record-h2").text.startswith(reservation):
                    for j, remove in enumerate(toolbar, start=1):
                        if j == i:
                            try:
                                element = remove.find_element(By.ID, 'btnCancella')
                            except NoSuchElementException:
                                return "error"
                            break
                    if found:
                        break
            element.click()
            confirm = self.driver.find_element(By.XPATH, "//*[@id='btnConferma']")
            confirm.click()
            return "success"
        except TimeoutError:
            return "timeout"

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