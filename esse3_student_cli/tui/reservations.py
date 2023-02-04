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

        def on_mount(self) -> None:
            self.table(self.reservation, self.index)

    class Line(Horizontal):

        def __init__(self, reservation) -> None:
            self.values = list(reservation.values())
            super().__init__()

        def on_mount(self) -> None:
            self.mount(self.Name(self.values[0]))
            self.mount(self.Check(self.values[0]))

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
        Binding(key="w", action="app.refresh('reservations')", description="refresh")
    ]

    async def fetch_date(self) -> None:
        """reservations = [{'name': 'BUSINESS GAME', '1': 'igikpwnygi', '2': 'jfsxfckizr', '3': 'rsyxjxhxgw', '4': 'otykbzckdf',
                          '5': 'ulxxftcxzp', '6': 'wlyztntjtl', '7': 'kjagclbcax', '8': 'pshhggmmxw',
                          '9': 'upbluuynsj'},
                        {'name': 'DATA ANALYTICS', '1': 'unqfqxmbbs', '2': 'wnjhosvbck', '3': 'azrprrbrgw', '4': 'vifbxzwefb',
                          '5': 'kmiehveaol', '6': 'rytpxgepda', '7': 'fyznnfjkrc', '8': 'ymkklaxmkj',
                          '9': 'cwzojlxgxf'},
                        {'name': "DIDATTICA DELL'INFORMATICA", '1': 'unqfqxmbbs', '2': 'wnjhosvbck', '3': 'azrprrbrgw',
                         '4': 'vifbxzwefb',
                         '5': 'kmiehveaol', '6': 'rytpxgepda', '7': 'fyznnfjkrc', '8': 'ymkklaxmkj',
                         '9': 'cwzojlxgxf'},
                        {'name': 'MOBILE', '1': 'unqfqxmbbs', '2': 'wnjhosvbck', '3': 'azrprrbrgw',
                         '4': 'vifbxzwefb',
                         '5': 'kmiehveaol', '6': 'rytpxgepda', '7': 'fyznnfjkrc', '8': 'ymkklaxmkj',
                         '9': 'cwzojlxgxf'},
                        {'name': 'GOOD', '1': 'unqfqxmbbs', '2': 'wnjhosvbck', '3': 'azrprrbrgw',
                         '4': 'vifbxzwefb',
                         '5': 'kmiehveaol', '6': 'rytpxgepda', '7': 'fyznnfjkrc', '8': 'ymkklaxmkj',
                         '9': 'cwzojlxgxf'}
                       ]"""
        reservations = cli.new_esse3_wrapper().fetch_reservations()
        await self.query_one(".reservations-loading").remove()
        if len(reservations) == 0:
            await self.query_one("#reservations-container").mount(Static(f"❌ No appeals booked !!", classes="reservations-removed-error"))
        else:
            await self.query_one("#reservations-container").mount(
                Vertical(id="reservations-vertical"),
                Static("Select exam to remove:", classes="title"),
                Container(id="reservations-buttons"),
            )
            for index, reservation in enumerate(reservations, start=1):
                self.query_one(Vertical).mount(self.Tables(reservation, index))
                await self.query_one("#reservations-buttons").mount(self.Line(reservation))
            await self.query_one("#reservations-container").mount(Horizontal(Button("send data", id="reservations-remove")))

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.fetch_date())

    def compose(self) -> ComposeResult:
        yield Header("Reservations", classes="header")
        yield Container(Static("List of Reservations", classes="title"),
                        Static("loading [#ec971f]exams booked[/] in progress.....", classes="reservations-loading"),
                        id="reservations-container")
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
            yield Container(Static("exam [#ec971f]booking removal[/] in progress.....", classes="reservations-loading"))
            yield Footer()

        BINDINGS = [
            Binding(key="r", action="app.reload('reservations')", description="return"),
            Binding(key="h", action="app.homepage('reservations')", description="homepage"),
        ]