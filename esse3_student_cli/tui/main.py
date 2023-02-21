from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Button, Footer
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual import events
from textual.pilot import Pilot

from esse3_student_cli.tui.booklet import Booklet
from esse3_student_cli.tui.exams import Exams
from esse3_student_cli.tui.reservations import Reservations
from esse3_student_cli.tui.taxes import Taxes


class Header(Static):
    pass


class HomePage(Screen):

    def compose(self) -> ComposeResult:
        yield Header("Homepage", classes="header")
        yield Container(
            Static("Commands:", classes="title"),
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

        name_value = "add-" + name

        if not self.is_screen_installed(name_value):
            self.install_screen(Exams.AddExams(exams), name=name_value)
        self.push_screen(name_value)

        for c in self.query("Checkbox"):
            c.value = False

        if self.is_screen_installed("reservations"):
            self.uninstall_screen("reservations")
        if self.is_screen_installed("remove-"+name_value):
            self.uninstall_screen("remove-"+name_value)

    def remove_reservation(self) -> None:
        name = None
        entro = False
        exams = []
        for c in self.query("Checkbox"):
            if c.value:
                name = c.name_value
                exams.append(name)
                entro = True
        if not entro:
            return

        if not self.is_screen_installed("reservations-removed"):
            self.install_screen(Reservations.RemoveReservation(exams), name="reservations-removed")
        self.push_screen("reservations-removed")

        for c in self.query("Checkbox"):
            c.value = False

        if self.is_screen_installed("exams"):
            self.uninstall_screen("exams")
        if self.is_screen_installed("add-"+name):
            self.uninstall_screen("add-"+name)

    async def on_key(self, event: events.Key):
        if event.key == "up" or event.key == "left":
            pilot = Pilot(self)
            await pilot.press("shift+tab")
        if event.key == "down" or event.key == "right":
            pilot = Pilot(self)
            await pilot.press("tab")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        screens = {"booklet": Booklet(), "reservations": Reservations(), "taxes": Taxes(), "exams": Exams()}
        commands = ["booklet", "reservations", "taxes", "exams"]
        booklet_buttons = ["average", "clear", "degree", "votes", "compute-average", "compute-vote", "compute-degree"]
        if event.button.id == "exams-send":
            self.add_exams()
        elif event.button.id == "reservations-remove":
            self.remove_reservation()
        else:
            if event.button.id not in commands and event.button.id not in booklet_buttons:
                if not self.is_screen_installed("remove-"+event.button.id):
                    self.install_screen(Reservations.RemoveReservation(event.button.id), name="remove-"+event.button.id)
                    self.push_screen("remove-"+event.button.id)
                else:
                    self.push_screen("remove-"+event.button.id)
                if self.is_screen_installed("exams"):
                    self.uninstall_screen("exams")
                if self.is_screen_installed("add-" + event.button.id):
                    self.uninstall_screen("add-" + event.button.id)
            elif event.button.id not in booklet_buttons:
                if not self.is_screen_installed(f"{event.button.id}"):
                    self.install_screen(screens[f"{event.button.id}"], name=f"{event.button.id}")
                    self.push_screen(f"{event.button.id}")
                else:
                    self.push_screen(f"{event.button.id}")

    def action_key_escape(self) -> None:
        self.exit()

    def action_refresh(self, screen):
        screens = {"booklet": Booklet(), "reservations": Reservations(), "taxes": Taxes(), "exams": Exams()}
        self.pop_screen()
        self.uninstall_screen(screen)
        self.install_screen(screens[f"{screen}"], name=f"{screen}")
        self.push_screen(screen)

    def action_reload(self, screen):
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
