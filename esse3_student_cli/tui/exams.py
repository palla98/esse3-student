import asyncio

from esse3_student_cli import cli

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
            await self.query_one("#exams-container").mount(Vertical(id="exams-table"))
            await self.query_one("#exams-container").mount(Container(
                # Input(placeholder="Notes...", id="exams-input"),
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
        yield Container(Static("List of available exams", classes="title"),
                        Static("loading [#ec971f]available exams[/] in progress.....", classes="exams-loading"),
                        id="exams-container"
                        )
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
            self.query_one(Container).mount \
                (Static(f"Exams: [green]{', '.join(map(str, self.exams))}[/] added", id="exams-added-success"))

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
