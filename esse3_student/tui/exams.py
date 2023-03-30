import asyncio

from esse3_student import cli
from esse3_student.primitives import ExamName, Date, SigningUp, Description

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Button, Footer, Checkbox
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen

from rich import box
from rich.table import Table


class Header(Static):
    pass


class Exams(Screen):

    class Tables(Static):

        def __init__(self, exams: list) -> None:
            self.exams = exams
            super().__init__()

        def on_mount(self) -> None:
            self.get_table(self.exams)

        def get_table(self, exams: list) -> None:

            table = Table(box=box.SIMPLE_HEAD, style="rgb(139,69,19)")
            table.add_column("#", justify="center", style="bold red")
            table.add_column("Name", justify="center", style="bold cyan")
            table.add_column("Date", justify="center", style="bold green")
            table.add_column("Signing up", justify="center", style="bold yellow")
            table.add_column("Description", justify="center", style="bold #f7ecb5")

            for index, (name, date, signing_up, description) in enumerate(exams, start=1):
                table.add_row(str(index), name.value, date.value, signing_up.value, description.value)

            self.update(table)

    class Line(Horizontal):

        def __init__(self, exam) -> None:
            self.value = exam
            super().__init__()

        def on_mount(self) -> None:
            self.mount(self.Name(self.value[0].value))
            self.mount(self.Check(self.value[0].value))

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
    ]

    async def fetch_date(self) -> None:
        """exams = [(ExamName(value='BUSINESS GAME'), Date(value='08/02/2023'), SigningUp(value='18/01/2023 - 06/02/2023'), Description(value='MDCS 6 ECTS')),
                 (ExamName(value='DATA ANALYTICS'), Date(value='06/02/2023'), SigningUp(value='23/12/2022 - 04/02/2023'), Description(value='Secondo appello')),
                 (ExamName(value='NETWORK SECURITY'), Date(value='07/02/2023'), SigningUp(value='05/01/2023 - 06/02/2023'), Description(value='Oral exam and project discussion')),
                 (ExamName(value='THEORETICAL COMPUTER SCIENCE'), Date(value='28/01/2023'), SigningUp(value='13/01/2023 - 27/01/2023'), Description(value='Prova orale con alcune domande scritte')),
                ]"""
        global wrapper
        try:
            wrapper = cli.new_esse3_wrapper()
        except:
            await self.query_one(".exams-loading").remove()
            await self.query_one(".reservations-container").mount(Static("Login failed !!!", classes="login-failed"))

        exams = wrapper.fetch_exams()
        await self.query_one(".exams-loading").remove()
        if len(exams) == 0:
            await self.query_one(".reservations-container").mount(Static("No exams available !!!", id="exams-empty"))
        else:
            await self.query_one(".reservations-container").mount(
                Vertical(id="exams-table"),
                Static("Select the checkboxes of the exams to be added:", classes="title"),
                Container(classes="reservations-buttons"),
            )
            await self.query_one("#exams-table").mount(self.Tables(exams))
            for index, exam in enumerate(exams, start=1):
                await self.query_one(".reservations-buttons").mount(self.Line(exam))
            await self.query_one(".reservations-container").mount(Horizontal(Button("book", id="add")))


    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.fetch_date())

    def compose(self) -> ComposeResult:
        yield Header("Exams", classes="header")
        yield Container(Static("List of available exams:", classes="title"),
                        Static("loading [yellow]available exams[/] in progress.....", classes="exams-loading"),
                        classes="reservations-container"
                        )
        yield Footer()

    class Add(Screen):

        def __init__(self, exams) -> None:
            self.exams = exams
            super().__init__()

        async def fetch_date(self) -> None:
            added, click = cli.new_esse3_wrapper().add(self.exams)
            await self.query_one(".exams-loading").remove()
            self.query_one(Container).mount \
                (Static(f"Exams: [green]{', '.join(map(str, added))}[/] added\n"
                        f"\n[bold]click saved: [blue]{click}", id="exams-added-success"))

        async def on_mount(self) -> None:
            await asyncio.sleep(0.1)
            asyncio.create_task(self.fetch_date())

        def compose(self) -> ComposeResult:
            yield Header("Exam added", classes="header")
            yield Container(Static("adding [yellow]reservations[/] in progress.....", classes="exams-loading"))
            yield Footer()

        BINDINGS = [
            Binding(key="r", action="app.return('exams')", description="return"),
            Binding(key="h", action="app.homepage('exams')", description="homepage"),
        ]
