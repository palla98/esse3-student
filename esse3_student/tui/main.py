from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Button, Footer
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual import events
from textual.pilot import Pilot

from esse3_student.primitives import ExamName
from esse3_student.tui.booklet import Booklet
from esse3_student.tui.exams import Exams
from esse3_student.tui.reservations import Reservations
from esse3_student.tui.taxes import Taxes


class Header(Static):
    pass


class HomePage(Screen):

    def compose(self) -> ComposeResult:
        yield Header("Homepage", classes="header")
        yield Container(
            Static("[bold][green]Esse3 command line utility[/green][/bold] :computer:", classes="title"),
            Vertical(
                Button("[bold]Booklet[/] - [italic]show all activities[/]", id="booklet"),
                Button("[bold]Taxes[/] - [italic]show all taxes[/]", id="taxes"),
                Button("[bold]Exams[/] - [italic]show available exams[/]", id="exams"),
                Button("[bold]Reservations[/] - [italic]show booked exams[/]", id="reservations"),
            ),
            id="homepage"
        )
        yield Footer()


class Tui(App):

    CSS_PATH = "style.css"

    SCREENS = {"homepage": HomePage()}

    BINDINGS = [
        Binding(key="escape", action="key_escape", description="exit"),
    ]

    def on_mount(self) -> None:
        self.push_screen("homepage")

    def modify(self, action: str) -> None:
        selected_exam_name = None
        at_least_one_checkbox_selected = False
        selected_exams = []
        for checkbox in self.query("Checkbox"):
            if checkbox.value:
                selected_exam_name = checkbox.name_value
                selected_exams.append(ExamName(selected_exam_name))
                at_least_one_checkbox_selected = True
        if not at_least_one_checkbox_selected:
            return

        name_value = f"{action}-{selected_exam_name}"

        if action == "add":
            if not self.is_screen_installed(name_value):
                self.install_screen(Exams.Add(selected_exams), name=name_value)
        elif action == "remove":
            if not self.is_screen_installed(name_value):
                self.install_screen(Reservations.Remove(selected_exams), name=name_value)

        self.push_screen(name_value)

        for c in self.query("Checkbox"):
            c.value = False

        if action == "add":
            if self.is_screen_installed("reservations"):
                self.uninstall_screen("reservations")
            if self.is_screen_installed("remove-" + selected_exam_name):
                self.uninstall_screen("remove-" + selected_exam_name)
        else:
            if self.is_screen_installed("exams"):
                self.uninstall_screen("exams")
            if self.is_screen_installed("add-" + selected_exam_name):
                self.uninstall_screen("add-" + selected_exam_name)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        screens = {"booklet": Booklet(), "reservations": Reservations(), "taxes": Taxes(), "exams": Exams()}
        changes = ["add", "remove"]
        if event.button.id in changes:
            self.modify(event.button.id)

        elif event.button.id in screens:
            if not self.is_screen_installed(f"{event.button.id}"):
                self.install_screen(screens[f"{event.button.id}"], name=f"{event.button.id}")
                self.push_screen(f"{event.button.id}")
            else:
                self.push_screen(f"{event.button.id}")

    async def on_key(self, event: events.Key):
        if event.key == "up":
            pilot = Pilot(self)
            await pilot.press("shift+tab")
        if event.key == "down":
            pilot = Pilot(self)
            await pilot.press("tab")

    def action_key_escape(self) -> None:
        self.exit()

    def action_return(self, screen):
        screens = {"booklet": Booklet(), "reservations": Reservations(), "taxes": Taxes(), "exams": Exams()}
        self.uninstall_screen(self.pop_screen())
        self.pop_screen()
        self.uninstall_screen(screen)
        self.install_screen(screens[f"{screen}"], name=f"{screen}")
        self.push_screen(screen)

    def action_homepage(self, screen):
        self.pop_screen()
        self.pop_screen()
        self.uninstall_screen(screen)
