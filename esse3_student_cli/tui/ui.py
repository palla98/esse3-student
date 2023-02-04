import asyncio
import time

from esse3_student_cli.primitives import Exam, ExaminationProcedure, ExamNotes, Vote, Cfu
from esse3_student_cli import cli
from typing import Tuple

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Button, Footer, Input, Checkbox
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen

from rich import box
from rich.text import Text
from rich.table import Table


class Header(Static):
    pass


class Booklet(Screen):

    exams = None

    class Tables(Static):

        def __init__(self, exams) -> None:
            self.exams = exams
            super().__init__()

        def on_mount(self):
            self.id = "booklet-table-exams"
            self.table(self.exams)

        def get_state(self, state: str) -> Text:
            colors = {"Superata": "green", "Frequenza attribuita d'ufficio": "yellow"}
            value = Text(state)
            value.stylize(f"{colors[state]}")
            return value

        def get_vote(self, vote: str) -> Text:
            colors = {"18": "bright_red", "19": "bright_red", "20": "bright_red", "21": "bright_red", \
                      "22": "yellow", "23": "yellow", "24": "yellow", "25": "yellow", \
                      "26": "blue", "27": "blue", "28": "blue", "29": "blue", "30": "blue", \
                      '': "white", "IDO": "green"}
            value = Text(vote)
            if value[0:3] == Text("IDO"):
                value = Text(str(value).replace("IDO", "IDONEO"))
            value.stylize(f"{colors[vote]}")

            return value

        def table(self, exams) -> None:

            table = Table(header_style="rgb(210,105,30) bold", box=box.SIMPLE_HEAD)
            table.add_column("#", style="red bold")
            table.add_column("Name", style="cyan bold")
            table.add_column("Academic Year", style="bold", justify="center")
            table.add_column("CFU", style="bold", justify="center")
            table.add_column("State", style="bold")
            table.add_column("Vote", style="bold")

            for index, exam in enumerate(exams, start=1):
                if index <= 15:
                    colums = exam.value.split("&")

                    state = self.get_state(colums[3])

                    vote_split = colums[4].split(" - ")
                    vote = self.get_vote(vote_split[0])

                    table.add_row(str(index), colums[0], colums[1], colums[2], state, vote)

            self.update(table)

    class Filter(Input):

        def __init__(self, field) -> None:
            self.field = field
            super().__init__()

        def on_mount(self):
            self.placeholder = self.field + "..."
            self.id = self.field

    class Average(Static):

        def __init__(self, averages) -> None:
            self.averages = averages
            super().__init__()

        def on_mount(self):
            self.table(self.averages)

        def table(self, averages):
            table = Table(header_style="rgb(255,204,51) bold", box=box.SIMPLE_HEAD)
            table.add_column("Average", style="bold", justify="center")
            table.add_column("Degree basis", style="bold", justify="center")
            values = averages[len(averages)-1].value.split("&")
            weighted = values[1]
            degree_basis = (float(weighted) * 11.0) / 3.0

            table.add_row(weighted, str(round(degree_basis, 2)))
            self.update(table)

    class NewAverage(Static):

        def __init__(self, averages, vote, cfu) -> None:
            self.averages = averages
            self.vote = vote
            self.cfu = cfu
            super().__init__()

        def on_mount(self):
            self.table(self.averages, self.vote, self.cfu)

        def table(self, averages, new_vote, new_cfu):
            table = Table(header_style="rgb(210,105,30) bold", box=box.SIMPLE_HEAD)
            table.add_column("Vote", style="bold", justify="center")
            table.add_column("Cfu", style="bold", justify="center")
            table.add_column("new average", style="bold", justify="center")
            table.add_column("New degree basis", style="bold", justify="center")
            values = averages[len(averages)-1].value.split("&")
            weighted = values[1]
            actual_average = float(weighted)
            actual_cfu = float(values[2])
            new_average = ((actual_average * actual_cfu) + (int(new_vote) * int(new_cfu))) / (actual_cfu + int(new_cfu))
            new_degree_basis = (new_average * 11.0) / 3.0

            table.add_row(str(new_vote), str(new_cfu), str(round(new_average, 2)), str(round(new_degree_basis, 2)))
            self.update(table)

    async def fetch_data(self) -> None:
        """self.exams = [
                    Exam.of("c1-riga1&c2-riga1&c3-riga1&c4-riga1"),
                    Exam.of("c1-riga2&c2-riga2&c3-riga2&c4-riga2"),
                    Exam.of("c1-riga3&c2-riga3&c3-riga3&c4-riga3"),
                    Exam.of("c1-riga4&c2-riga4&c3-riga4&c4-riga4"),
                    Exam.of("c1-riga4&ca2-riga4&c3-riga4&c4-riga4"),
                    Exam.of("c1-riga4&ca2-riga4&c3-riga4&c4_riga4"),
                    Exam.of("25.8&27.8&30"),
                ]"""
        self.exams = cli.new_esse3_wrapper().fetch_booklet()

        await self.query_one("#booklet-loading").remove()
        await self.query_one("#principale").mount(
            Vertical(self.Tables(self.exams))
        )
        await self.query_one("#principale").mount(
                            Static("Compute new average", classes="title"),
                            Container(
                                self.Average(self.exams),
                                Horizontal(
                                    self.Filter("vote"),
                                    self.Filter("cfu"),
                                    Button("compute", id="booklet-button"),
                                    id="booklet-filters"
                                ),
                                id="booklet-container-filters"
                            )
                        )

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.fetch_data())

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "booklet-button":
            try:
                element1 = self.query(self.NewAverage).last()
                element1.remove()
            except:
                pass
            try:
                element2 = self.query("#booklet-value-error").last()
                element2.remove()
            except:
                pass

            vote = self.query_one("#vote").value
            cfu = self.query_one("#cfu").value
            if vote != "" and cfu != "":
                try:
                    vote = Vote(int(vote)).value
                    cfu = int(Cfu(cfu).value)
                    self.query_one("#principale").mount(self.NewAverage(self.exams, vote, cfu))
                except ValueError:
                    self.query_one("#principale").mount(Static("Wrong values", id="booklet-value-error"))

    def compose(self) -> ComposeResult:
        yield Header("Booklet", classes="header")
        yield Container(
            Static("List passed exams", classes="title"),
            Static("[b][green]exam booklet[/] loading in progress.....[/]", id="booklet-loading"),
            id="principale"
        )
        yield Footer()

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
        Binding(key="w", action="app.refresh('booklet')", description="refresh")
    ]


class Taxes(Screen):

    class Tables(Static):

        def __init__(self, taxes) -> None:
            self.taxes = taxes
            super().__init__()

        def _on_mount(self) -> None:
            self.id = "taxes-table"
            self.table(self.taxes)

        def payment_changes(self, amount: str, payment_status) -> Tuple[str, str]:
            colors = {" pagato confermato": "rgb(50,205,50)", " non pagato": "red", " pagato": "rgb(0,100,0)"}
            names = {" pagato confermato": "payment confirmed", " non pagato": "to pay", " pagato": "refund"}
            value = Text(amount)
            value.stylize(f"{colors[payment_status]}")
            return value, names[payment_status]

        def table(self, taxes) -> None:

            table = Table(header_style="rgb(210,105,30) bold", box=box.SIMPLE_HEAD)
            table.add_column("#", style="red bold")
            table.add_column("ID", style="cyan bold")
            table.add_column("Expiration date", style="bold", justify="center")
            table.add_column("Amount", style="bold")
            table.add_column("Payment status", style="bold")

            for index, taxe in enumerate(taxes, start=1):
                colums = taxe.split("&")
                amount, payment = self.payment_changes(colums[2], colums[3])
                table.add_row(str(index), colums[0], colums[1], amount, payment)

            self.update(table)

    async def fetch_date(self) -> None:
        taxes = cli.new_esse3_wrapper().fetch_taxes()
        await self.query_one("#taxes-loading").remove()
        self.query_one(Container).mount(
            Vertical(
                self.Tables(taxes),
            )
        )

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.fetch_date())

    def compose(self) -> ComposeResult:
        yield Header("Taxes", classes="header")
        yield Container(
            Static("List of taxes", classes="title"),
            Static("taxes loading in progress.....", id="taxes-loading"),
        )
        yield Footer()

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
        Binding(key="w", action="app.refresh('taxes')", description="refresh")
    ]


class Exams(Screen):

    class Tables(Static):

        def __init__(self, exams: list) -> None:
            self.exams = exams
            super().__init__()

        def on_mount(self) -> None:
            self.get_table(self.exams)

        def get_table(self, exams: list) -> None:

            table = Table(box=box.HEAVY_HEAD, style="rgb(139,69,19)")
            table.add_column("#", justify="center", style="bold red")
            table.add_column("Name", justify="center", style="green")
            table.add_column("Date", justify="center", style="yellow")
            table.add_column("Signing up", justify="center", style="yellow")
            table.add_column("Description", justify="center")

            for index, exam in enumerate(exams, start=1):
                row = list(exam.value.split("&"))
                table.add_row(str(index), *row)

            self.update(table)

    class Line(Horizontal):

        def __init__(self, exam) -> None:
            self.value = list(exam.value.split("&"))
            super().__init__()

        def on_mount(self) -> None:
            self.mount(self.Name(self.value[0]))
            self.mount(self.Check(self.value[0]))

        class Name(Static):
            def __init__(self, name) -> None:
                self.value = name
                super().__init__()

            def on_mount(self) -> None:
                self.update(self.value)

        class Check(Checkbox):
            def __init__(self, value) -> None:
                self.name_value = value
                super().__init__()

            def on_mount(self) -> None:
                self.value = False
                self.id = self.name_value

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
        Binding(key="w", action="app.refresh('exams')", description="refresh")
    ]

    async def fetch_date(self) -> None:
        """exams = [
            ["colonna1-riga1", "colonna2-riga1", "colonna9-riga1", "colonna4-riga1"],
            ["colonna1-riga2", "colonna2-riga2", "colonna3-riga2", "colonna4-riga2"],
            ["colonna1-riga3", "colonna2-riga3", "colonna3-riga3", "colonna4-riga3"],
            ["colonna1-riga4", "colonna2-riga4", "colonna3-riga4", "colonna4-riga4"],
            ["colonna1-riga4", "colonna2-riga4", "colonna3-riga4", "colonna4-riga4"],
            ["colonna1-riga4", "colonna2-riga4", "colonna3-riga4", "colonna4_riga4"],
            ["colonna1-riga4", "colonna2-riga4", "colonna3-riga4", "colonna4_riga4"],
        ]"""
        exams = cli.new_esse3_wrapper().fetch_exams()
        await self.query_one(".exams-loading").remove()
        if len(exams) == 0:
            await self.query_one("#exams-container").mount(Static("no exams available !!", id="exams-empty"))
        else:
            await self.mount(Container(id="exams-container"))
            await self.query_one("#exams-container").mount(Static("List of available exams", classes="title"))
            await self.query_one("#exams-container").mount(Vertical(id="exams-table"))
            await self.query_one("#exams-container").mount(Container(
                #Input(placeholder="Notes...", id="exams-input"),
                Container(id="exams-checkbox"),
                id="exams-add"
            ))
            await self.query_one(Vertical).mount(self.Tables(exams))
            for index, exam in enumerate(exams, start=1):
                await self.query_one("#exams-checkbox").mount(self.Line(exam))
            await self.query_one("#exams-container").mount(Horizontal(Button("send data", id="exams-send")))

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.fetch_date())

    def compose(self) -> ComposeResult:
        yield Header("Exams", classes="header")
        yield Static("loading [yellow]available exams[/] in progress.....", classes="exams-loading")
        yield Footer()


class AddExams(Screen):

    def __init__(self, exams, modality, notes) -> None:
        self.exams = exams
        self.modality = modality
        self.notes = notes
        super().__init__()

    async def fetch_date(self) -> None:
        cli.new_esse3_wrapper().add_reservation(list(self.exams), self.modality, self.notes)
        await self.query_one(".exams-loading").remove()
        self.query_one(Container).mount(Static(f"Exams: [green]{', '.join(map(str, self.exams))}[/] added", id="exams-added-success"))

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.fetch_date())

    def compose(self) -> ComposeResult:
        yield Header("Exam added", classes="header")
        yield Container(Static("added [yellow]reservations[/] in progress.....", classes="exams-loading"))
        yield Footer()

    BINDINGS = [
        Binding(key="r", action="app.reload('exams')", description="return"),
        Binding(key="h", action="app.homepage('exams')", description="homepage"),
    ]


class Reservations(Screen):

    class Tables(Static):

        def __init__(self, reservation, index: int) -> None:
            self.reservation = reservation
            self.index = index
            super().__init__()

        def table(self, reservation, index: int):

            table = Table(box=box.HEAVY_HEAD, style="rgb(139,69,19)")
            table.add_column("#", justify="center", style="bold red")
            for colum in reservation.keys():
                if colum == "Name":
                    table.add_column(colum, justify="center", style="bold green")
                else:
                    table.add_column(colum, justify="center")

            row = list(reservation.values())
            table.add_row(str(index), *row)
            self.update(table)

        def on_mount(self) -> None:
            self.table(self.reservation, self.index)

    class Line(Horizontal):

        def __init__(self, reservation) -> None:
            self.values = list(reservation.values())
            super().__init__()

        def on_mount(self) -> None:
            self.mount(self.Name(self.values[0]))
            self.mount(self.Check(self.values[0]))

        class Name(Static):
            def __init__(self, name) -> None:
                self.value = name
                super().__init__()

            def on_mount(self) -> None:
                self.update(self.value)

        class Check(Checkbox):
            def __init__(self, value) -> None:
                self.name_value = value
                super().__init__()

            def on_mount(self) -> None:
                self.value = False
                self.id = self.name_value

    """class Buttons(Button):

        def __init__(self, reservation) -> None:
            self.reservation = reservation
            super().__init__()

        def value(self, reservation):
            colums = list(reservation.values())
            return colums[0]

        def on_mount(self) -> None:
            self.label = self.value(self.reservation)
            self.id = self.value(self.reservation)"""

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
        Binding(key="w", action="app.refresh('reservations')", description="refresh")
    ]

    async def fetch_date(self) -> None:
        reservations = [{'name': 'BUSINESS GAME', '1': 'igikpwnygi', '2': 'jfsxfckizr', '3': 'rsyxjxhxgw', '4': 'otykbzckdf',
                          '5': 'ulxxftcxzp', '6': 'wlyztntjtl', '7': 'kjagclbcax', '8': 'pshhggmmxw',
                          '9': 'upbluuynsj'},
                        {'name': 'DATA ANALYTICS', '1': 'unqfqxmbbs', '2': 'wnjhosvbck', '3': 'azrprrbrgw', '4': 'vifbxzwefb',
                          '5': 'kmiehveaol', '6': 'rytpxgepda', '7': 'fyznnfjkrc', '8': 'ymkklaxmkj',
                          '9': 'cwzojlxgxf'},
                        {'name': "DIDATTICA DELL'INFORMATICA", '1': 'unqfqxmbbs', '2': 'wnjhosvbck', '3': 'azrprrbrgw',
                         '4': 'vifbxzwefb',
                         '5': 'kmiehveaol', '6': 'rytpxgepda', '7': 'fyznnfjkrc', '8': 'ymkklaxmkj',
                         '9': 'cwzojlxgxf'},
                        {'name': 'MOBILE', '1': 'unqfqxmbbs', '2': 'wnjhosvbck', '3': 'azrprrbrgw',
                         '4': 'vifbxzwefb',
                         '5': 'kmiehveaol', '6': 'rytpxgepda', '7': 'fyznnfjkrc', '8': 'ymkklaxmkj',
                         '9': 'cwzojlxgxf'},
                        {'name': 'GOOD', '1': 'unqfqxmbbs', '2': 'wnjhosvbck', '3': 'azrprrbrgw',
                         '4': 'vifbxzwefb',
                         '5': 'kmiehveaol', '6': 'rytpxgepda', '7': 'fyznnfjkrc', '8': 'ymkklaxmkj',
                         '9': 'cwzojlxgxf'}
                       ]
        #reservations = cli.new_esse3_wrapper().fetch_reservations()
        await self.query_one(".reservations-loading").remove()
        if len(reservations) == 0:
            await self.query_one("#reservations-container").mount(Static(f"❌ No appeals booked !!", classes="reservations-removed-error"))
        else:
            await self.query_one("#reservations-container").mount(
                Static("List of Reservations", classes="title"),
                Vertical(id="reservations-vertical"),
                Static("Select exam to remove:", classes="title"),
                Container(id="reservations-buttons"),
            )
            for index, reservation in enumerate(reservations, start=1):
                self.query_one(Vertical).mount(self.Tables(reservation, index))
                await self.query_one("#reservations-buttons").mount(self.Line(reservation))
            await self.query_one("#reservations-container").mount(Horizontal(Button("send data", id="reservations-remove")))

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.fetch_date())

    def compose(self) -> ComposeResult:
        yield Header("Reservations", classes="header")
        yield Container(Static("loading [yellow]exams booked[/] in progress.....", classes="reservations-loading")
                        , id="reservations-container")
        yield Footer()


class RemoveReservation(Screen):

    def __init__(self, reservation) -> None:
        self.reservation = reservation
        super().__init__()

    async def fetch_date(self) -> None:
        result = cli.new_esse3_wrapper().remove_reservation(self.reservation)
        await self.query_one(".reservations-loading").remove()
        if result == "success":
            self.query_one(Container).mount(Static(f"Reservation: {self.reservation} removed", id="reservations-removed-success"))
        elif result == "empty":
            self.query_one(Container).mount(Static(f"❌ No exams to remove !!", classes="reservations-removed-error"))
        else:
            self.query_one(Container).mount(Static(f"❌ Impossible to remove: {self.reservation} cause subscription closed", classes="reservations-removed-error"))

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.fetch_date())

    def compose(self) -> ComposeResult:
        yield Header("Reservation removed", classes="header")
        yield Container(Static("exam booking removal in progress.....", classes="reservations-loading"))
        yield Footer()

    BINDINGS = [
        Binding(key="r", action="app.reload('reservations')", description="return"),
        Binding(key="h", action="app.homepage('reservations')", description="homepage"),
    ]


class HomePage(Screen):

    def compose(self) -> ComposeResult:
        yield Header("Homepage", classes="header")
        yield Container(
            Static("Commands", classes="title"),
            Vertical(
                Button("Booklet", id="booklet"),
                Button("Taxes", id="taxes"),
                Button("Exams", id="exams"),
                Button("Reservations", id="reservations"),
            ),
            id="homepage"
        )
        yield Footer()


class Tui(App):

    CSS_PATH = "ui.css"

    SCREENS = {"homepage": HomePage()}

    BINDINGS = [
        Binding(key="escape", action="key_escape", description="exit"),
        Binding(key="s", action="light_mode_toggle", description="light mode"),
    ]

    def on_mount(self) -> None:
        self.push_screen("homepage")

    def add_exams(self) -> None:
        name = None
        entro = False
        exams = []
        for c in self.query("Checkbox"):
            if c.value:
                name = c.name_value
                exams.append(name)
                entro = True
                #break
        if not entro:
            return

        """n = ""
        for c in self.query("Input"):
            if c.value != "":
                n = c.value
                break
        if n != "":
            notes = ExamNotes(n)
        else:
            notes = ExamNotes(" ")"""

        name_value = "add-" + name

        if not self.is_screen_installed(name_value):
            self.install_screen(AddExams(exams, ExaminationProcedure("P"), ExamNotes(" ")), name=name_value)
        self.push_screen(name_value)

        for c in self.query("Input"):
            c.value = ""

        for c in self.query("Checkbox"):
            c.value = False

        if self.is_screen_installed("reservations"):
            self.uninstall_screen("reservations")
        if self.is_screen_installed("remove-"+name_value):
            self.uninstall_screen("remove-"+name_value)

    def remove_reservation(self) -> None:
        name = None
        entro = False
        for c in self.query("Checkbox"):
            if c.value:
                name = c.name_value
                entro = True
                break
        if not entro:
            return

        name_value = "remove-" + name

        if not self.is_screen_installed(name_value):
            self.install_screen(RemoveReservation(name), name=name_value)
        self.push_screen(name_value)

        for c in self.query("Checkbox"):
            c.value = False
            c.refresh()

        if self.is_screen_installed("exams"):
            self.uninstall_screen("exams")
        if self.is_screen_installed("add-"+name_value):
            self.uninstall_screen("add-"+name_value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        screens = {"booklet": Booklet(), "reservations": Reservations(), "taxes": Taxes(), "exams": Exams()}
        commands = ["booklet", "reservations", "taxes", "exams"]
        if event.button.id == "exams-send":
            self.add_exams()
        elif event.button.id == "reservations-remove":
            self.remove_reservation()
        else:
            if event.button.id not in commands and event.button.id != "booklet-button":
                if not self.is_screen_installed("remove-"+event.button.id):
                    self.install_screen(RemoveReservation(event.button.id), name="remove-"+event.button.id)
                    self.push_screen("remove-"+event.button.id)
                else:
                    self.push_screen("remove-"+event.button.id)
                if self.is_screen_installed("exams"):
                    self.uninstall_screen("exams")
                if self.is_screen_installed("add-" + event.button.id):
                    self.uninstall_screen("add-" + event.button.id)
            elif event.button.id != "booklet-button":
                if not self.is_screen_installed(f"{event.button.id}"):
                    self.install_screen(screens[f"{event.button.id}"], name=f"{event.button.id}")
                    self.push_screen(f"{event.button.id}")
                else:
                    self.push_screen(f"{event.button.id}")

    def action_key_escape(self) -> None:
        self.exit()

    def action_light_mode_toggle(self) -> None:
        self.dark = not self.dark

    def action_refresh(self, screen):
        screens = {"booklet": Booklet(), "reservations": Reservations(), "taxes": Taxes(), "exams": Exams()}
        self.pop_screen()
        self.uninstall_screen(screen)
        self.install_screen(screens[f"{screen}"], name=f"{screen}")
        self.push_screen(screen)

    def action_reload(self, screen):
        screens = {"booklet": Booklet(), "reservations": Reservations(), "taxes": Taxes(), "exams": Exams()}
        self.pop_screen()
        self.pop_screen()
        self.uninstall_screen(screen)
        self.install_screen(screens[f"{screen}"], name=f"{screen}")
        self.push_screen(screen)

    def action_homepage(self, screen):
        self.pop_screen()
        self.pop_screen()
        self.uninstall_screen(screen)
