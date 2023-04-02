import asyncio

from esse3_student.primitives import Cfu, Grade
from esse3_student import cli

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Button, Footer, Input
from textual.containers import Container, Vertical
from textual.screen import Screen

from rich import box
from rich.text import Text
from rich.table import Table


class Header(Static):
    pass


def get_status(status: str) -> Text:
    colors = {"Passed": "green", "Ex officio assigned frequency": "#f7ecb5"}
    value = Text(status)
    value.stylize(f"{colors[status]}")

    return value


def get_grade(grade: str) -> Text:
    colors = {"18": "bright_red", "19": "bright_red", "20": "bright_red", "21": "bright_red",
              "22": "yellow", "23": "yellow", "24": "yellow", "25": "yellow",
              "26": "blue", "27": "blue", "28": "blue", "29": "blue", "30": "blue",
              '': "white", "...": "white", "ELIGIBLE": "green"}
    value = Text(grade)
    value.stylize(f"{colors[grade]}")

    return value


class Booklet(Screen):

    exams = None
    statistics = None

    class Tables(Static):

        def __init__(self, exams) -> None:
            self.exams = exams
            super().__init__()

        def on_mount(self):
            self.id = "booklet-table-exams"
            self.table(self.exams)

        def table(self, exams) -> None:

            table = Table(style="rgb(139,69,19) bold", box=box.SIMPLE_HEAD)
            table.add_column("#", style="red bold")
            table.add_column("Name", style="cyan bold")
            table.add_column("Academic Year", style="bold", justify="center")
            table.add_column("CFU", style="bold", justify="center")
            table.add_column("Status", style="bold")
            table.add_column("Grade", style="bold", justify="center")
            table.add_column("Date", style="#E1C699 bold", justify="center")

            for index, (name, year, cfu, status, grade, date) in enumerate(exams, start=1):
                name, year, cfu, status, grade, date = map(lambda x: x.value, (name, year, cfu, status, grade, date))

                status = get_status(status)
                grade = get_grade(grade)

                table.add_row(str(index), name, str(year), cfu, status, grade, date)

            self.update(table)

    class ActualAverage(Static):

        def __init__(self, averages) -> None:
            self.averages = averages
            super().__init__()

        def on_mount(self):
            self.table(self.averages)

        def table(self, averages):
            table = Table(header_style="rgb(255,204,51) bold", box=box.SIMPLE_HEAD)
            table.add_column("Actual Average", style="bold", justify="center")
            table.add_column("Actual Degree basis", style="bold", justify="center")

            actual_average, actual_cfu  = averages
            degree_basis = (float(actual_average) * 11) / 3

            table.add_row(str(actual_average), str(round(degree_basis, 2)))
            self.update(table)

    class NewAverage(Static):

        def __init__(self, averages) -> None:
            self.averages = averages
            super().__init__()

        def compose(self) -> ComposeResult:
            yield Container(
                Static("[b]What average would you like to have?[/]"),
                Input(placeholder="average..", id="average"),
                Static("[b]How many cfu do you still have available?[/]"),
                Input(placeholder="cfu...", id="cfu"),
                Button("[b]compute[/]", classes="compute", id="compute-average"),
                classes="booklet-container-filters",
            )

        def on_button_pressed(self, event: Button.Pressed):

            if event.button.id == "compute-average":
                buttons = ["#result", "#booklet-value-error"]
                for element in buttons:
                    try:
                        self.query(element).last().remove()
                    except:
                        pass
                average_to_achieve = self.query_one("#average").value
                remaining_cfu = self.query_one("#cfu").value
                if average_to_achieve != "" and remaining_cfu != "":
                    try:

                        average_to_achieve = Grade(int(average_to_achieve)).value
                        remaining_cfu = int(remaining_cfu)

                        actual_average, actual_cfu = self.averages

                        total_cfu = remaining_cfu + actual_cfu

                        grade_to_obtain = ((average_to_achieve * total_cfu) - (actual_average * actual_cfu)) \
                                          / float(remaining_cfu)

                        self.query_one(".booklet-container-filters").mount(Static(f"[b]The grade you need to take \n"
                                                                                  f"for each upcoming exam\n"
                                                                                  f"having [yellow]{remaining_cfu} cfu available[/]: "
                                                                                  f"[green]{str(round(grade_to_obtain, 2))}", id="result"))

                    except ValueError:
                        self.query_one(".booklet-container-filters").mount(
                            Static("[red][bold]Wrong values[/]", id="booklet-value-error"))

    class NewGrade(Static):

        def __init__(self, averages) -> None:
            self.averages = averages
            super().__init__()

        def compose(self) -> ComposeResult:
            yield Container(
                Static("[b]What grade do you think you get?[/]"),
                Input(placeholder="grade...", id="grade"),
                Static("[b]How many CFU does the exam have?[/]"),
                Input(placeholder="cfu...", id="cfu"),
                Button("[b]compute[/]", classes="compute", id="compute-grade"),
                classes="booklet-container-filters",
            )

        def on_button_pressed(self, event: Button.Pressed):

            if event.button.id == "compute-grade":
                buttons = ["#result", "#booklet-value-error"]
                for element in buttons:
                    try:
                        self.query(element).last().remove()
                    except:
                        pass
                grade = self.query_one("#grade").value
                cfu = self.query_one("#cfu").value
                if grade != "" and cfu != "":
                    try:
                        grade = Grade(int(grade)).value
                        cfu = int(Cfu(cfu).value)
                        actual_average, actual_cfu = self.averages
                        new_average = ((actual_average * actual_cfu) + (int(grade) * int(cfu))) / (
                                actual_cfu + int(cfu))
                        new_degree_basis = (new_average * 11.0) / 3.0

                        self.query_one(".booklet-container-filters").mount(Static(
                            f"[b][yellow]New Average:[/] {round(new_average, 2)}/30\n[yellow]New Degree basis:[/] "
                            f"{round(new_degree_basis, 2)}/110[/]",
                            id="result"))

                    except ValueError:
                        self.query_one(".booklet-container-filters").mount(
                            Static("[red][bold]Wrong values[/]", id="booklet-value-error"))

    async def fetch_data(self) -> None:

        global wrapper
        try:
            wrapper = cli.new_esse3_wrapper()
        except:
            await self.query_one("#booklet-loading").remove()
            await self.query_one("#booklet-container").mount(Static("Login failed !!!", classes="login-failed"))

        self.exams, self.statistics = wrapper.fetch_booklet()

        await self.query_one("#booklet-loading").remove()
        await self.query_one("#booklet-container").mount(
            Vertical(self.Tables(self.exams))
        )
        await self.query_one("#booklet-container").mount(
                            Static("Planning:", classes="title"),
                            Container(
                                self.ActualAverage(self.statistics),
                                Button("Plan a new average", id="average"),
                                Button("Projects a new grade", id="grade"),
                                Button("clear", id="clear"),
                                classes="booklet-container-options"
                            ),
                        )

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.fetch_data())

    def compose(self) -> ComposeResult:
        yield Header("Booklet", classes="header")
        yield Container(
            Static("Exams:", classes="title"),
            Static("[b][yellow]exams booklet[/] loading in progress....[/]", id="booklet-loading"),
            id="booklet-container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):

        elements_to_remove = [self.NewAverage, self.NewGrade]
        compute_buttons = ["compute-average", "compute-grade"]

        if event.button.id == "clear":
            for element in elements_to_remove:
                try:
                    self.query(element).last().remove()
                except:
                    pass
            return

        if event.button.id not in compute_buttons:
            for element in elements_to_remove:
                try:
                    self.query(element).last().remove()
                except:
                    pass

        if event.button.id == "average":
            self.query_one("#booklet-container").mount(self.NewAverage(self.statistics))

        if event.button.id == "grade":
            self.query_one("#booklet-container").mount(self.NewGrade(self.statistics))

        if event.button.id == "degree":
            self.query_one("#booklet-container").mount(self.NewDegree(self.exams))

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
    ]