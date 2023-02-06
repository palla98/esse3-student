import asyncio

from esse3_student_cli.primitives import Vote, Cfu
from esse3_student_cli import cli

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Button, Footer, Input
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
            colors = {"Superata": "green", "Frequenza attribuita d'ufficio": "#f7ecb5"}
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

            table = Table(style="rgb(139,69,19) bold", box=box.SIMPLE_HEAD)
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
            table.add_column("Actual Average", style="bold", justify="center")
            table.add_column("Actual Degree basis", style="bold", justify="center")
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
            table = Table(header_style="rgb(255,204,51) bold", box=box.SIMPLE_HEAD)
            table.add_column("Vote", style="bold", justify="center")
            table.add_column("Cfu", style="bold", justify="center")
            table.add_column("New Average", style="bold", justify="center")
            table.add_column("New Degree basis", style="bold", justify="center")
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
                            Static("Compute new average:", classes="title"),
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
            Static("Booklet exams:", classes="title"),
            Static("[b][yellow]exams booklet[/] loading in progress.....[/]", id="booklet-loading"),
            id="principale"
        )
        yield Footer()

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
        Binding(key="w", action="app.refresh('booklet')", description="refresh")
    ]