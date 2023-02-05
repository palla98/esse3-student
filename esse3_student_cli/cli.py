import dataclasses
import time

import typer
from typing import List, Tuple, Optional
from rich import box
from rich.progress import track
from rich.table import Table
from rich.text import Text

from esse3_student_cli.esse3_wrapper import Esse3Wrapper
from esse3_student_cli.primitives import ExaminationProcedure, ExamNotes, AcademicYear, ExamState, Vote, Cfu, Year, Exam

from esse3_student_cli.utils.console import console


@dataclasses.dataclass(frozen=True)
class AppOptions:
    username: str = dataclasses.field(default='')
    password: str = dataclasses.field(default='')
    debug: bool = dataclasses.field(default=False)


app_options = AppOptions()
app = typer.Typer()


def is_debug_on():
    return app_options.debug


def run_app():
    try:
        app()
    except Exception as e:
        if is_debug_on():
            raise e
        else:
            console.print(f"[red bold]Error:[/red bold] {e}")


def new_esse3_wrapper(detached: bool = False, with_live_status: bool = True):
    def res():
        return Esse3Wrapper.create(
            username=app_options.username,
            password=app_options.password,
            debug=app_options.debug,
            detached=detached,
            headless=not app_options.debug and not detached,
        )
    if with_live_status:
        with console.status("Login..."):
            return res()
    return res()


@app.callback()
def main(
        username: str = typer.Option(..., prompt=True, envvar="CLI_STUDENT_USERNAME"),
        password: str = typer.Option(..., prompt=True, hide_input=True, envvar="CLI_STUDENT_PASSWORD"),
        #username: str = typer.Option(show_default=False, default=take_credentials("username"), help="default credentials in file"),
        #password: str = typer.Option(show_default=False, default=take_credentials("password"), help="default credentials in file"),
        debug: bool = typer.Option(False, "--debug", help="Don't minimize browser"),
):

    global app_options
    app_options = AppOptions(
        username=username,
        password=password,
        debug=debug,
    )


@app.command(name="exams")
def command_exams() -> None:

    """
    Available exams list
    """

    esse_wrapper = new_esse3_wrapper()
    with console.status("loading available exams..."):
        exams = esse_wrapper.fetch_exams()

    if len(exams) == 0:
        console.print("No exams available!", style="bold red")
        exit()

    console.rule("EXAMS")

    table = Table(box=box.HEAVY_HEAD, style="rgb(139,69,19)")
    table.add_column("#", justify="center", style="bold red")
    table.add_column("Name", justify="center", style="green")
    table.add_column("Date", justify="center", style="yellow")
    table.add_column("Signing up", justify="center", style="yellow")
    table.add_column("Description", justify="center")

    for index, exam in enumerate(exams, start=1):
        row = list(exam.value.split("&"))
        table.add_row(str(index), *row)

    console.print(table)


@app.command(name="reservations")
def command_reservations() -> None:

    """
    Available reservations list
    """

    esse_wrapper = new_esse3_wrapper()
    with console.status("loading available reservations..."):
        reservations = esse_wrapper.fetch_reservations()
        if len(reservations) == 0:
            console.print("No exam booked!", style="bold red")
            exit()

    console.rule("Reservations showcase")
    tables = {}
    for index in range(len(reservations)):
        tables[f'table_{index}'] = Table(box=box.HEAVY_HEAD)
        tables[f'table_{index}'].add_column("#", justify="center", style="bold red")
        for colum in reservations[index].keys():
            tables[f'table_{index}'].add_column(colum, justify="center")

    for index, reservation in enumerate(reservations, start=0):
        row = list(reservation.values())
        tables[f'table_{index}'].add_row(str(index+1), *row)
        console.print(tables[f'table_{index}'])


@app.command(name="add_reservation")
def command_add_reservation(
        exams: str = typer.Argument(
            ...,
            metavar="Exams name",
            help='A string of the form: "name1-name2...." or "name1" for single value'
        ),
):

    def parse(exams) -> []:
        values = exams.split("-")
        try:
            for v in values:
                Exam(v)
        except ValueError:
            console.print("Invalid name or names")
            raise typer.Exit()

        return values

    names = parse(exams)

    esse_wrapper = new_esse3_wrapper()

    with console.status(f"[bold green]Exams booking[/] in progress..."):
        time.sleep(3)
        value = esse_wrapper.add_reservation(list(names))
        if value == "ok":
            console.log(f"[bold] ✅ Exams with name: [green]{', '.join(map(str, names))}[/] added")
        elif value == "empty":
            console.print("No exams available!", style="bold yellow")


@app.command(name="remove_reservation")
def command_remove_reservation(
        reservations: str = typer.Argument(
            ...,
            metavar="Reservations name",
            help='A string of the form: "name1-name2...." or "name1" for single value'
        ),

):
    def parse(reservations) -> list:
        values = []
        try:
            for r in reservations.split("-"):
                values.append(Exam(r).value)
        except ValueError:
            console.print("[bold red]Invalid characters[/]")
            raise typer.Exit()

        return values

    names = parse(reservations)

    esse3_wrapper = new_esse3_wrapper()

    with console.status(f"[bold][green]Search reservations[/] to remove in progress....[/]"):
        time.sleep(3)
        values = esse3_wrapper.remove_reservation(list(names))

        if len(values) == 0:
            console.log(f"[bold]❌ No exams to remove or wrong values passed[/]!!!")
        else:
            all_success = True
            all_closed = True
            for i in values.keys():
                if i == 0:
                    all_success = False
                else:
                    all_closed = False

            if all_closed:
                console.log(f"[bold]❌ Impossible to remove: [red]{', '.join([x for x in values[0]])}[/] cause subscription closed[/]")
            elif all_success:
                console.log(f"[bold]Reservations: [green]{', '.join([x for x in values[1]])}[/] removed[/]")
            else:
                console.log(f"[bold]✅ Reservations: [green]{', '.join([x for x in values[1]])}[/] removed[/]")
                console.log(f"[bold]❌ Impossible to remove: [red]{', '.join([x for x in values[0]])}[/] cause subscription closed[/]")


@app.command(name="booklet")
def command_booklet(
        academic_year: int = typer.Option(int, help="academic year (1 to 5)"),
        exam_state: str = typer.Option(str, help="'Superata' as Passed or 'Frequenza attribuita d'ufficio' as Failed"),
        vote: int = typer.Option(int, help="vote of the exam"),
        new_average: Tuple[int, str] = typer.Option((None, None), help="calculate new average: (vote cfu); ex: 25 12"),
) -> None:

    """
    All carrier exams
    """

    if academic_year:
        try:
            academic_year = AcademicYear(academic_year)
        except ValueError:
            console.print("Invalid year")
            raise typer.Exit()

    if exam_state:
        try:
            exam_state = ExamState(exam_state)
        except ValueError:
            console.print("Invalid exam state")
            raise typer.Exit()

    if vote:
        try:
            vote = Vote(vote)
        except ValueError:
            console.print("Invalid vote")
            raise typer.Exit()

    if new_average[1]:
        try:
            new_vote = Vote(int(new_average[0])).value
        except ValueError:
            console.print("Invalid vote value")
            raise typer.Exit()
        try:
            new_cfu = int(Cfu(new_average[1]).value)
        except ValueError:
            console.print("Invalid cfu value")
            raise typer.Exit()

    esse3_wrapper = new_esse3_wrapper()
    with console.status("Fetching exams booklet..."):
        exams = esse3_wrapper.fetch_booklet()

    table = Table(header_style="rgb(210,105,30) bold", box=box.SIMPLE_HEAD)
    table.add_column("#", style="red bold")
    table.add_column("Name", style="cyan bold")
    table.add_column("Academic Year", style="bold", justify="center")
    table.add_column("CFU", style="bold", justify="center")
    table.add_column("State", style="bold")
    table.add_column("Vote", style="bold")

    def get_state_color(state):
        colors = {"Superata":"green", "Frequenza attribuita d'ufficio":"yellow"}
        return colors[state]

    def get_vote_color(vote):
        colors = {"18":"bright_red", "19":"bright_red", "20":"bright_red", "21":"bright_red",\
                  "22":"yellow", "23":"yellow", "24":"yellow", "25":"yellow",\
                  "26":"blue", "27":"blue", "28":"blue", "29":"blue", "30":"blue", \
                  '':"white", "IDO":"green"}
        return colors[vote]

    for index, exam in enumerate(track(exams, description="Processing...", transient=True), start=1):
        colums = exam.value.split("&")
        if len(colums) != 3:
            c = get_state_color(colums[3])
            vote_split = colums[4].split(" - ")
            v = get_vote_color(vote_split[0])
            vote_style = Text(colums[4])
            if vote_style[0:3] == Text("IDO"):
                vote_style = Text(str(vote_style).replace("IDO", "IDONEO"))
                vote_style.stylize(f"bold {v}", 0, 6)
            else:
                vote_style.stylize(f"bold {v}", 0, 2)
            if academic_year:
                if colums[1] == str(academic_year.value):
                    table.add_row(str(index), colums[0], colums[1], colums[2], f'[{c}]{colums[3]}[/{c}]', vote_style)
            elif exam_state:
                if colums[3] == exam_state.value:
                    table.add_row(str(index), colums[0], colums[1], colums[2], f'[{c}]{colums[3]}[/{c}]', vote_style)
            elif vote:
                if colums[4][0:2] == str(vote.value):
                    table.add_row(str(index), colums[0], colums[1], colums[2], f'[{c}]{colums[3]}[/{c}]', vote_style)
            else:
                table.add_row(str(index), colums[0], colums[1], colums[2], f'[{c}]{colums[3]}[/{c}]', vote_style)

        time.sleep(0.1)

    console.rule("[bold]Booklet[/bold]")
    console.print(table)

    table = Table(header_style="rgb(210,105,30) bold", box=box.SIMPLE_HEAD)
    table.add_column("Arithmetic average", style="bold", justify="center")
    table.add_column("Weighted average", style="bold", justify="center")
    table.add_column("Degree basis", style="bold", justify="center")
    averages = exams[len(exams)-1].value.split("&")
    arithmetic = averages[0]
    weighted = averages[1]
    degree_basis = (float(weighted)*11.0)/3.0
    if new_average[1] is not None:
        table.add_column("Vote", style="bold", justify="center")
        table.add_column("Cfu", style="bold", justify="center")
        table.add_column("new average", style="bold", justify="center")
        table.add_column("New degree basis", style="bold", justify="center")
        actual_average = float(weighted)
        actual_cfu = float(averages[2])
        new = ((actual_average*actual_cfu)+(new_vote*new_cfu)) / (actual_cfu+new_cfu)
        new_degree_basis = (new * 11.0) / 3.0

        table.add_row(arithmetic, weighted, str(round(degree_basis, 2)), str(new_vote),
                      str(new_cfu), str(round(new, 2)), str(round(new_degree_basis, 2)))
    else:
        table.add_row(arithmetic, weighted, str(round(degree_basis, 2)))

    if not academic_year and not vote and not exam_state:
        console.rule("[bold]Statistics[/bold]")
        console.print(table)


@app.command(name="taxes")
def command_taxes(
        to_pay: Optional[bool] = typer.Option(False, "--to-pay", help="Show all taxes to be paid"),
        year: int = typer.Option(int, help="es: '2021'; filter taxes by year"),
) -> None:

    """
    All taxes
    """

    if year:
        try:
            year = Year(year)
        except ValueError:
            console.print("Invalid year value")
            raise typer.Exit()

    esse3_wrapper = new_esse3_wrapper()
    with console.status("Fetching taxes..."):
        taxes = esse3_wrapper.fetch_taxes()

    table = Table(header_style="rgb(210,105,30) bold", box=box.SIMPLE_HEAD)
    table.add_column("#", style="red bold")
    table.add_column("ID", style="cyan bold")
    table.add_column("Expiration date", style="bold", justify="center")
    table.add_column("Amount", style="bold")
    table.add_column("Payment status", style="bold")

    def payment_changes(payment_status) -> Tuple[str, str]:
        colors = {" pagato confermato": "rgb(50,205,50)", " non pagato": "red", " pagato": "rgb(0,100,0)"}
        names = {" pagato confermato": "payment confirmed", " non pagato": "to pay", " pagato": "refund"}
        return names[payment_status], colors[payment_status]

    for index, taxe in enumerate(track(taxes, description="Processing...", transient=True), start=1):
        colums = taxe.split("&")
        payment_status, c = payment_changes(colums[3])
        year_date = colums[1].split("-")

        if to_pay and year:
            if year_date[0] == str(year.value) and payment_status == "to pay":
                table.add_row(str(index), colums[0], colums[1], f'[{c}]{colums[2]}[/{c}]', payment_status)
        elif to_pay:
            if payment_status == "to pay":
                table.add_row(str(index), colums[0], colums[1], f'[{c}]{colums[2]}[/{c}]', payment_status)
        elif year:
            if year_date[0] == str(year.value):
                table.add_row(str(index), colums[0], colums[1], f'[{c}]{colums[2]}[/{c}]', payment_status)
        else:
            table.add_row(str(index), colums[0], colums[1], f'[{c}]{colums[2]}[/{c}]', payment_status)

        time.sleep(0.1)

    console.rule("[bold]Taxes[/bold]")
    console.print(table)


@app.command(name="tui")
def tui() -> None:
    from esse3_student_cli.tui.main import Tui
    # faccio l import qua perchè altrimenti: from textual.app import App, ComposeResult, RenderResult, mi apre
    # un socket nonostante non lanci il run
    Tui().run()


