import asyncio

from esse3_student_cli.primitives import Exam, ExaminationProcedure, ExamNotes
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

    class Tables(Static):

        def __init__(self, exams) -> None:
            self.exams = exams
            super().__init__()

        def on_mount(self):
            self.id = "booklet-table"
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
                colums = exam.value.split("&")

                state = self.get_state(colums[3])

                vote_split = colums[4].split(" - ")
                vote = self.get_vote(vote_split[0])

                table.add_row(str(index), colums[0], colums[1], colums[2], state, vote)

            self.update(table)

    async def fetch_data(self) -> None:
        exams = cli.new_esse3_wrapper().fetch_booklet()
        await self.query_one("#booklet-loading").remove()
        self.query_one(Container).mount(
            Vertical(
                self.Tables(exams),
            )
        )

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.fetch_data())

    def compose(self) -> ComposeResult:
        yield Header("Booklet", classes="header")
        yield Container(
            Static("List passed exams", classes="title"),
            Static("exam booklet loading in progress.....", id="booklet-loading"),
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

        def _on_mount(self) -> None:
            self.get_table(self.exams)

        def get_table(self, exams: list) -> None:

            table = Table(box=box.HEAVY_HEAD, style="rgb(139,69,19)")
            table.add_column("#", justify="center", style="bold red")
            colums = exams[0].value.split("&")
            if len(colums) == 2:
                table.add_column("Name", justify="center", style="green")
                table.add_column("Date", justify="center", style="yellow")
            else:
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

        def _on_mount(self) -> None:
            self.mount(self.Name(self.value[0]))
            self.mount(self.Check(self.value[0]))

        class Name(Static):
            def __init__(self, name) -> None:
                self.value = name
                super().__init__()

            def _on_mount(self) -> None:
                self.update(self.value)

        class Check(Checkbox):
            def __init__(self, value) -> None:
                self.parameter = value
                super().__init__()

            def _on_mount(self) -> None:
                self.value = False

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
        Binding(key="w", action="app.refresh('exams')", description="refresh")
    ]

    async def fetch_date(self) -> None:
        """exams = [
            ["colonna1_riga1", "colonna2_riga1", "colonna9_riga1", "colonna4_riga1"],
            ["colonna1_riga2", "colonna2_riga2", "colonna3_riga2", "colonna4_riga2"],
            ["colonna1_riga3", "colonna2_riga3", "colonna3_riga3", "colonna4_riga3"],
            ["colonna1_riga4", "colonna2_riga4", "colonna3_riga4", "colonna4_riga4"],
            ["colonna1_riga4", "colonna2_riga4", "colonna3_riga4", "colonna4_riga4"],
            ["colonna1_riga4", "colonna2_riga4", "colonna3_riga4", "colonna4_riga4"],
            ["colonna1_riga4", "colonna2_riga4", "colonna3_riga4", "colonna4_riga4"],
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
                Input(placeholder="Notes...", id="exams-input"),
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
        yield Static("loading available exams in progress.....", classes="exams-loading")
        yield Footer()

    class AddExams(Screen):

        def __init__(self, exam, modality, notes) -> None:
            self.exam = exam
            self.modality = modality
            self.notes = notes
            super().__init__()

        async def fetch_date(self) -> None:
            result = cli.new_esse3_wrapper().add_reservation(self.exam, self.modality, self.notes)
            await self.query_one(".exams-loading").remove()
            if result == "ok":
                self.query_one(Container).mount(Static(f"Exam: {self.exam} added", id="exams-added-success"))
            elif result == "name error":
                self.query_one(Container).mount(Static(f"❌ Wrong name passed !!", classes="exams-added-error"))
            elif result == "empty":
                self.query_one(Container).mount(Static(f"❌ No exams to add !!", classes="exams-added-error"))

        async def on_mount(self) -> None:
            await asyncio.sleep(0.1)
            asyncio.create_task(self.fetch_date())

        def compose(self) -> ComposeResult:
            yield Header("Exam added", classes="header")
            yield Container(Static("added reservation in progress.....", classes="exams-loading"))
            yield Footer()

        BINDINGS = [
            Binding(key="r", action="app.pop_screen", description="return")
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

        def _on_mount(self) -> None:
            self.table(self.reservation, self.index)

    class Buttons(Button):

        def __init__(self, reservation) -> None:
            self.reservation = reservation
            super().__init__()

        def value(self, reservation):
            colums = list(reservation.values())
            return colums[0]

        def _on_mount(self) -> None:
            self.label = self.value(self.reservation)
            self.id = self.value(self.reservation)

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
        Binding(key="w", action="app.refresh('reservations')", description="refresh")
    ]

    async def fetch_date(self) -> None:
        reservations = cli.new_esse3_wrapper().fetch_reservations()
        await self.query_one(".reservations-loading").remove()
        if len(reservations) == 0:
            self.query_one(Container).mount(Static(f"❌ No appeals booked !!", classes="reservations-removed-error"))
        else:
            self.query_one(Container).mount(
                Static("List of Reservations", classes="title"),
                Vertical(id="vertical"),
                Static("Select exam to remove:", classes="title"),
                Horizontal(id="horizontal"),
            )
            for index, reservation in enumerate(reservations, start=1):
                self.query_one(Vertical).mount(self.Tables(reservation, index))
                self.query_one(Horizontal).mount(self.Buttons(reservation))

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.fetch_date())

    def compose(self) -> ComposeResult:
        yield Header("Reservations", classes="header")
        yield Container(Static("loading exams booked in progress.....", classes="reservations-loading"))
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
        Binding(key="r", action="app.pop_screen", description="return")
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        screens = {"booklet": Booklet(), "reservations": Reservations(), "taxes": Taxes(), "exams": Exams()}
        buttons = ["booklet", "reservations", "taxes", "exams"]
        if event.button.id == "exams-send":
            for c in self.query("Checkbox"):
                if c.value:
                    name = Exam(c.parameter)
                    break
            if self.query_one("#exams-input").value == "":
                notes = ExamNotes(" ")
            else:
                notes = ExamNotes(self.query_one("#exams-input").value)
            if not self.is_screen_installed(f"{name.value}"):
                self.install_screen(Exams.AddExams(name, ExaminationProcedure("P"), notes), name=f"{name.value}")
            self.push_screen(f"{name.value}")
        else:
            if not self.is_screen_installed(f"{event.button.id}") and event.button.id not in buttons:
                self.install_screen(RemoveReservation(event.button.id), name=f"{event.button.id}")
            elif not self.is_screen_installed(f"{event.button.id}"):
                self.install_screen(screens[f"{event.button.id}"], name=f"{event.button.id}")
            self.push_screen(f"{event.button.id}")

    def action_refresh(self, screen) -> None:
        screens = {"booklet": Booklet(), "reservations": Reservations(), "taxes": Taxes(), "exams": Exams()}
        self.pop_screen()
        self.uninstall_screen(screen)
        self.install_screen(screens[f"{screen}"], name=f"{screen}")
        self.push_screen(screen)

    def action_key_escape(self) -> None:
        self.exit()

    def action_light_mode_toggle(self) -> None:
        self.dark = not self.dark


