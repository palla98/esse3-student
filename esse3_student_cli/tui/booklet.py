import asyncio

from esse3_student_cli.primitives import Vote, Cfu, Exam
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
            table.add_column("Status", style="bold")
            table.add_column("Grade", style="bold", justify="center")

            for index, exam in enumerate(exams, start=1):
                if index <= 15:
                    colums = exam.value.split("&")

                    state = self.get_state(colums[3])

                    vote_split = colums[4].split(" ")
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
            table.add_column("Grade", style="bold", justify="center")
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
            Exam(value='27007802 - AGILE SOFTWARE DEVELOPMENT&1&6&Superata&23 - 31/01/2022'),
            Exam(value='27008537 - ALGORITHMIC GAME THEORY&1&6&Superata&30 - 25/02/2022'),
            Exam(value="27006172 - CRYPTOGRAPHY&1&6&Frequenza attribuita d'ufficio&"),
            Exam(value="27007791 - DATA ANALYTICS&1&12&Frequenza attribuita d'ufficio&"),
            Exam(value="27007399 - NETWORK SECURITY&1&6&Frequenza attribuita d'ufficio&"),
            Exam(value='27006179 - SECURE SOFTWARE DESIGN&1&6&Superata&23 - 19/01/2022'),
            Exam(value="27006163 - THEORETICAL COMPUTER SCIENCE&1&12&Frequenza attribuita d'ufficio&"),
            Exam(value="27005226 - ASPETTI ETICI E GIURIDICI DELL’INFORMATICA&2&6&Frequenza attribuita d'ufficio&"),
            Exam(value="27000275 - BUSINESS GAME&2&6&Frequenza attribuita d'ufficio&"),
            Exam(value='27008777 - CYBER OFFENSE AND DEFENSE&2&6&Superata&27 - 31/01/2023'),
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
                                Button("Schedule Average", id="average"),
                                Button("Schedule Degree basis", id="degree"),
                                Button("project grade", id="votes"),
                                Button("clear", id="clear"),
                                #Horizontal(
                                 #   self.Filter("vote"),
                                  #  self.Filter("cfu"),
                                   # Button("compute", id="booklet-button"),
                                    #id="booklet-filters"
                                #),
                                classes="booklet-container-options"
                            ),
                        )

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.fetch_data())

    def on_button_pressed(self, event: Button.Pressed):

        if event.button.id == "clear":
            try:
                element2 = self.query(".booklet-container-filters").last()
                element2.remove()
            except:
                pass
            return

        if event.button.id == "average":
            try:
                element2 = self.query(".booklet-container-filters").last()
                element2.remove()
            except:
                pass

            self.query_one("#principale").mount(
                                Container(
                                    Static("[b]Che media vorresti avere?[/]"),
                                    Input(placeholder="media..."),
                                    Static("[b]Quanti cfu hai ancora a disposizione?[/]"),
                                    Input(placeholder="cfu..."),
                                    Button("[b]compute[/]", classes="compute", id="compute-average"),
                                    classes="booklet-container-filters",
                                ),
            )

        if event.button.id == "compute-average":
            self.query_one(".booklet-container-filters").mount(Static("cssss"))

        if event.button.id == "votes":
            try:
                element2 = self.query(".booklet-container-filters").last()
                element2.remove()
            except:
                pass

            self.query_one("#principale").mount(
                                Container(
                                    Static("[b]What grade do you think you get?[/]"),
                                    Input(placeholder="grade...", id="vote"),
                                    Static("[b]How many CFU does the exam have?[/]"),
                                    Input(placeholder="cfu...", id="cfu"),
                                    Button("[b]compute[/]", classes="compute", id="compute-vote"),
                                    classes="booklet-container-filters",
                                ),
            )

        if event.button.id == "compute-vote":
            vote = self.query_one("#vote").value
            cfu = self.query_one("#cfu").value
            if vote != "" and cfu != "":
                try:
                    vote = Vote(int(vote)).value
                    cfu = int(Cfu(cfu).value)
                    values = self.exams[len(self.exams) - 1].value.split("&")
                    weighted = values[1]
                    actual_average = float(weighted)
                    actual_cfu = float(values[2])
                    new_average = ((actual_average * actual_cfu) + (int(vote) * int(cfu))) / (
                                actual_cfu + int(cfu))
                    new_degree_basis = (new_average * 11.0) / 3.0
                    try:
                        element2 = self.query_one("#result")
                        element2.remove()
                    except:
                        pass
                    try:
                        element2 = self.query_one("#booklet-value-error")
                        element2.remove()
                    except:
                        pass
                    self.query_one(".booklet-container-filters").mount(Static(f"[b][yellow]New Average:[/] {round(new_average, 2)}/30\n[yellow]New Degree basis:[/] {round(new_degree_basis, 2)}/110[/]", id="result"))
                except ValueError:
                    try:
                        element2 = self.query_one("#booklet-value-error")
                        element2.remove()
                    except:
                        pass
                    try:
                        element2 = self.query_one("#result")
                        element2.remove()
                    except:
                        pass
                    self.query_one(".booklet-container-filters").mount(Static("[red]Wrong values[/]", id="booklet-value-error"))

        if event.button.id == "degree":
            try:
                element2 = self.query(".booklet-container-filters").last()
                element2.remove()
            except:
                pass

            self.query_one("#principale").mount(
                                Horizontal(
                                    Static("[b]Che voto di laurea vorresti avere?[/]"),
                                    Input(placeholder="66-110", id="base"),
                                    Static("[b]Quanti cfu hai ancora?[/]"),
                                    Input(placeholder="n° CFU", id="CFU"),
                                    Button("[b]compute[/]", classes="compute", id="compute-degree"),
                                    classes="booklet-container-filters"
                                ),
            )

        if event.button.id == "compute-degree":
            pass


    def compose(self) -> ComposeResult:
        yield Header("Booklet", classes="header")
        yield Container(
            Static("Booklet exams:", classes="title"),
            Static("[b][yellow]exams booklet[/] loading in progress....[/]", id="booklet-loading"),
            id="principale"
        )
        yield Footer()

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
        Binding(key="w", action="app.refresh('booklet')", description="refresh")
    ]