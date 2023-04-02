import dataclasses
import time
import typer

from typing import Tuple
from rich import box
from rich.progress import track
from rich.table import Table
from rich.text import Text

from esse3_student.esse3_wrapper import Esse3Wrapper
from esse3_student.primitives import AcademicYear, ExamStatus, Cfu, Year, ExamName, Grade
from esse3_student.utils.console import console

from typing import Optional


@dataclasses.dataclass(frozen=True)
class AppOptions:
    username: str = dataclasses.field(default='')
    password: str = dataclasses.field(default='')
    debug: bool = dataclasses.field(default=False)


app_options = AppOptions()
app = typer.Typer(rich_markup_mode="rich", add_completion=False)


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
        with console.status("[bold]Login....[/]"):
            return res()
    return res()


@app.callback()
def main(
        username: str = typer.Option(..., prompt=True, envvar="CLI_STUDENT_USERNAME"),
        password: str = typer.Option(..., "--password", prompt=True, hide_input=True, envvar="CLI_STUDENT_PASSWORD"),
        debug: bool = typer.Option(False, "--debug", help="To show browser operations"),
):

    """
    [bold][green]Esse3 command line utility[/green][/bold] :computer:
    """

    global app_options
    app_options = AppOptions(
        username=username,
        password=password,
        debug=debug,
    )


@app.command(name="exams")
def command_exams() -> None:

    """
    [bold][#E1C699]Show available exams list[/][/bold] :bookmark_tabs:
    """

    esse_wrapper = new_esse3_wrapper()
    with console.status("[bold]Retrieval of [green]available exams[/green] in progress[/]",
                        spinner="aesthetic"):
        time.sleep(2)
        exams = esse_wrapper.fetch_exams()

    if len(exams) == 0:
        console.print("No exams available!!!", style="bold red")
        exit()

    console.rule("[bold]EXAMS SHOWCASE[/]")

    table = Table(box=box.SIMPLE_HEAD, style="rgb(139,69,19)", leading=1)
    table.add_column("#", justify="center", style="bold red")
    table.add_column("Name", justify="center", style="bold cyan")
    table.add_column("Date", justify="center", style="bold green")
    table.add_column("Signing up", justify="center", style="bold yellow")
    table.add_column("Description", justify="center", style="bold #f7ecb5")

    for index, (name, date, signing_up, description) in enumerate(exams, start=1):
        table.add_row(str(index), name.value, date.value, signing_up.value, description.value)

    console.print(table, justify="center")
    console.rule("[bold]STATISTICS[/]", style="yellow")
    console.print("\n[bold]clicks saved: [blue]7[/]\n", justify="center")


@app.command(name="reservations")
def command_reservations() -> None:

    """
    [bold][#E1C699]Show exams booked list[/][/bold] :bookmark_tabs:
    """

    esse_wrapper = new_esse3_wrapper()
    with console.status("[bold]Fetching [green]available reservations[/] in progress....[/]", spinner="aesthetic"):
        time.sleep(2)
        reservations = esse_wrapper.fetch_reservations()
        if len(reservations) == 0:
            console.print("No exams booked!!!", style="bold red")
            exit()

    console.rule("[bold]RESERVATIONS SHOWCASE[/]")
    tables = {}
    for index in range(len(reservations)):
        tables[f'table_{index}'] = Table(box=box.SIMPLE_HEAD, style="rgb(139,69,19)")
        tables[f'table_{index}'].add_column("#", justify="center", style="bold red")
        for colum in reservations[index].keys():
            if colum == "Name":
                tables[f'table_{index}'].add_column(colum, justify="center", style="bold cyan", no_wrap=True)
            elif colum == "Date":
                tables[f'table_{index}'].add_column(colum, justify="center", style="bold yellow")
            elif colum == "Cancella Prenotazione":
                tables[f'table_{index}'].add_column(colum, justify="center", style="bold red")
            else:
                tables[f'table_{index}'].add_column(colum, justify="center", style="bold #f7ecb5")

    for index, reservation in enumerate(reservations, start=0):
        row = list(reservation.values())
        tables[f'table_{index}'].add_row(str(index+1), *row)
        console.print(tables[f'table_{index}'], justify="center")

    console.rule("[bold]STATISTICS[/]", style="yellow")
    console.print("\n[bold]clicks saved: [blue]7[/]\n", justify="center")


@app.command(name="add")
def command_add(
        exams: list[str] = typer.Argument(
            ...,
            metavar="exam names",
            help="[bold]one or more strings of the form 'add name1 name2ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss'"
        ),
):
    """
    [bold][#E1C699]Operation that allows the [green]booking[/green] of examinations[/][/bold] :blue_book:
    """

    def parse(exams: list) -> list[ExamName]:
        try:
            exams_list = [ExamName(v) for v in exams]
        except ValueError:
            console.print("[bold red]Invalid strings[/]")
            raise typer.Exit()

        return exams_list

    values = parse(exams)

    esse_wrapper = new_esse3_wrapper()

    with console.status(f"[bold]Exams [green]booking[/] in progress....[/]", spinner="aesthetic"):
        exams, click = esse_wrapper.add(list(values))
        values = [i.value for i in exams]
        if len(values) == 0:
            console.print("No exams available or wrong names passed!!!\n", style="bold red")
        else:
            console.log(f"[bold] ✅ Exams with name: [green]{', '.join(map(str, values))}[/] added\n")

    console.rule("[bold]STATISTICS[/]", style="yellow")
    console.print(f"\n[bold]clicks saved: [blue]{click}[/]\n", justify="center")


@app.command(name="remove")
def command_remove_reservation(
        reservations: list[str] = typer.Argument(
            ...,
            metavar="Reservations name",
            help="[bold]one or more strings of the form 'remove name1 name2'"
        ),

):

    """
    [bold][#E1C699]Operation that allows the [red]deletion[/red] of booked examinations[/][/bold] :wastebasket:
    """

    def parse(reservations: list) -> list[ExamName]:
        try:
            exams_list = [ExamName(v) for v in reservations]
        except ValueError:
            console.print("[bold red]Invalid strings[/]")
            raise typer.Exit()

        return exams_list

    values = parse(reservations)

    esse3_wrapper = new_esse3_wrapper()

    with console.status(f"[bold]Searching [green]reservations[/] to remove in progress....[/]", spinner="aesthetic"):
        time.sleep(2)
        values, click = esse3_wrapper.remove(list(values))

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
                console.log(
                    f"[bold]❌ Impossible to remove: [red]{', '.join([x for x in values[0]])}[/] cause subscription closed or wrong names passed[/]")
            elif all_success:
                console.log(f"[bold]Reservations: [green]{', '.join([x for x in values[1]])}[/] removed\n[/]")
            else:
                console.log(f"[bold]✅ Reservations: [green]{', '.join([x for x in values[1]])}[/] removed[/]")
                console.log(
                    f"[bold]❌ Impossible to remove: [red]{', '.join([x for x in values[0]])}[/] cause subscription closed or wrong names passed[/]")

    console.rule("[bold]STATISTICS[/]", style="yellow")
    console.print(f"\n[bold]clicks saved: [blue]{click}[/]\n", justify="center")


@app.command(name="booklet")
def command_booklet(
        academic_year: int = typer.Option(int, help="[bold]Academic year (1 to 3)"),
        exam_status: str = typer.Option(..., help="[bold]'[green]Superata[/]' like 'Passed' or '[yellow]Frequenza attribuita d'ufficio[/]' like 'To do'[/]"),
        exam_grade: int = typer.Option(int, help="[bold]Grade of the exam[/]"),
        new_average: Tuple[int, str] = typer.Option((None, None), help="[bold]calculate new average with grade: (grade cfu); ex: '25 12' [/]"),
        #new_degree: Tuple[int, str] = typer.Option((None, None), help="[bold]calculate new average with remaining cfu: (degree cfu); ex: '27 12' [/]"),
        statistics: Optional[bool] = typer.Option(False, "--statistics", "-s", help="[bold]show statistics on the average"),
        #prova: int = typer.Argument(int, help="caaooooooooooooooooooooo"), #valore predefinito è zero in questo caso
) -> None:

    """
    [bold][#E1C699]shows all the student's activities[/][/bold] :bookmark_tabs:
    """

    if academic_year:
        try:
            academic_year = AcademicYear(academic_year)
        except ValueError:
            console.print("[bold yellow]Invalid year[/]")
            raise typer.Exit()

    if exam_status:
        try:
            exam_status = ExamStatus(exam_status)
        except ValueError:
            console.print("[bold yellow]Invalid exam status[/]")
            raise typer.Exit()

    if exam_grade:
        try:
            exam_grade = Grade(exam_grade)
        except ValueError:
            console.print("[bold yellow]Invalid grade[/]")
            raise typer.Exit()

    new_vote = None
    new_cfu = None
    if new_average[1]:
        try:
            new_vote = Grade(int(new_average[0])).value
        except ValueError:
            console.print("[bold yellow]Invalid vote value[/]")
            raise typer.Exit()
        try:
            new_cfu = int(Cfu(new_average[1]).value)
        except ValueError:
            console.print("[bold yellow]Invalid cfu value[/]")
            raise typer.Exit()

    esse3_wrapper = new_esse3_wrapper()
    with console.status("[bold]Fetching [green]exams booklet[/] in progress....[/]", spinner="aesthetic"):
        exams, averages = esse3_wrapper.fetch_booklet()

    table = Table(style="rgb(139,69,19) bold", box=box.SIMPLE_HEAD)
    table.add_column("#", style="red bold")
    table.add_column("Name", style="cyan bold")
    table.add_column("Academic Year", style="bold", justify="center")
    table.add_column("CFU", style="bold", justify="center")
    table.add_column("Status", style="bold")
    table.add_column("Grade", style="bold", justify="center")
    table.add_column("Date", style="#E1C699 bold", justify="center")

    def get_status_color(status):
        colors = {"Passed": "green", "Ex officio assigned frequency": "yellow"}
        return colors[status]

    def get_grade_color(grade):
        colors = {"18": "bright_red", "19": "bright_red", "20": "bright_red", "21": "bright_red",
                  "22": "yellow", "23": "yellow", "24": "yellow", "25": "yellow",
                  "26": "blue", "27": "blue", "28": "blue", "29": "blue", "30": "blue",
                  '': "white", "...": "white", "ELIGIBLE": "green"}
        return colors[grade]

    for index, (name, year, cfu, status, grade, date) in enumerate(exams, start=1):

        name, year, cfu, status, grade, date = map(lambda x: x.value, (name, year, cfu, status, grade, date))

        status_color = get_status_color(status)
        grade_color = get_grade_color(grade)

        grade_style = Text(grade)
        grade_style.stylize(f"{grade_color}")

        if academic_year and year != academic_year.value:
            continue
        if exam_status and status != exam_status.value:
            continue
        if exam_grade and grade[0:2] != str(exam_grade.value):
            continue

        table.add_row(str(index), name, str(year), cfu, f'[{status_color}]{status}[/{status_color}]',
                      grade_style, date)

    console.rule("[bold]BOOKLET SHOWCASE[/bold]")
    console.print(table, justify="center")

    table = Table(header_style="rgb(210,105,30) bold", box=box.SIMPLE_HEAD)
    table.add_column("Weighted average", style="bold", justify="center")
    table.add_column("Degree basis", style="bold", justify="center")

    actual_average, actual_cfu = averages
    degree_basis = (actual_average * 11) / 3

    if new_average[1] is not None:
        table.add_column("Grade", style="bold", justify="center")
        table.add_column("Cfu", style="bold", justify="center")
        table.add_column("New Average", style="bold", justify="center")
        table.add_column("New Degree Basis", style="bold", justify="center")

        new = ((actual_average * actual_cfu) + (new_vote * new_cfu)) / (actual_cfu + new_cfu)
        new_degree_basis = (new * 11) / 3

        table.add_row(str(actual_average), str(round(degree_basis, 2)), str(new_vote),
                      str(new_cfu), str(round(new, 2)), str(round(new_degree_basis, 2)))
    else:
        table.add_row(str(actual_average), str(round(degree_basis, 2)))

    if statistics:
        console.print(table, justify="center")
    console.rule("[bold]STATISTICS[/bold]")
    console.print("\n[bold]clicks saved: [blue]7[/]\n", justify="center")


@app.command(name="taxes")
def command_taxes(
        payment: str = typer.Option(str, help="[bold]Shows taxes by status type: ('to pay'|'confirmed'|'refund')"),
        year: int = typer.Option(int, "--year", "-y", help="[bold]filter taxes by year; es: '2021'"),
) -> None:

    """
    [bold][#E1C699]Show all taxes[/][/bold] :bookmark_tabs:
    """

    if year:
        try:
            year = Year(year).value
        except ValueError:
            console.print("Invalid year value")
            raise typer.Exit()

    esse3_wrapper = new_esse3_wrapper()
    with console.status("[bold]Fetching [green]taxes[/] in progress....[/]", spinner="aesthetic"):
        taxes, click = esse3_wrapper.fetch_taxes()

    table = Table(style="rgb(139,69,19) bold", box=box.SIMPLE_HEAD)
    table.add_column("#", style="red bold")
    table.add_column("ID", style="cyan bold")
    table.add_column("Expiration date", style="bold yellow", justify="center")
    table.add_column("Amount", style="bold")
    table.add_column("Payment status", style="bold #f7ecb5")

    def payment_changes(payment_status) -> Tuple[str, str]:
        colors = {" pagato confermato": "rgb(50,205,50)", " non pagato": "red", " pagato": "rgb(0,100,0)"}
        names = {" pagato confermato": "payment confirmed", " non pagato": "to pay", " pagato": "refund"}
        return names[payment_status], colors[payment_status]

    for index, (id, date, amount, status) in enumerate(track(taxes, description="[bold]Processing....[/]", transient=True), start=1):
        id, date, amount, status = map(lambda x: x.value, (id, date, amount, status))
        payment_status, c = payment_changes(status)

        if payment in payment_status and str(year) in date:
            table.add_row(str(index), id, date, f'[{c}]{amount}[/{c}]', payment_status)

        elif payment:
            if payment in payment_status:
                table.add_row(str(index), id, date, f'[{c}]{amount}[/{c}]', payment_status)

        elif year:
            if str(year) in date:
                table.add_row(str(index), id, date, f'[{c}]{amount}[/{c}]', payment_status)

        else:
            table.add_row(str(index), id, date, f'[{c}]{amount}[/{c}]', payment_status)

    console.rule("[bold]TAXES SHOWCASE[/bold]")
    console.print(table, justify="center")
    console.rule("[bold]STATISTICS[/]", style="yellow")
    console.print(f"\n[bold]clicks saved: [blue]{click}[/]\n", justify="center")


@app.command(name="tui")
def tui() -> None:

    """
    [bold][#E1C699]Run [yellow]text-user-interface[/yellow][/][/bold]
    """
    from esse3_student.tui.main import Tui

    Tui().run()


