import asyncio

from esse3_student_cli import cli
from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static, Footer
from textual.containers import Container, Vertical
from textual.screen import Screen

from rich import box
from rich.text import Text
from rich.table import Table


class Header(Static):
    pass


class Taxes(Screen):

    class Tables(Static):

        def __init__(self, taxes) -> None:
            self.taxes = taxes
            super().__init__()

        def on_mount(self) -> None:
            self.id = "taxes-table"
            self.table(self.taxes)

        def payment_changes(self, amount: str, payment_status) -> tuple[Text, Any]:
            colors = {" pagato confermato": "rgb(50,205,50)", " non pagato": "red", " pagato": "rgb(0,100,0)"}
            names = {" pagato confermato": "payment confirmed", " non pagato": "to pay", " pagato": "refund"}
            value = Text(amount)
            value.stylize(f"{colors[payment_status]}")
            return value, names[payment_status]

        def table(self, taxes) -> None:

            table = Table(header_style="rgb(210,105,30) bold", box=box.SIMPLE_HEAD)
            table.add_column("#", style="red bold")
            table.add_column("ID", style="cyan bold")
            table.add_column("Expiration date", style="bold", justify="center")
            table.add_column("Amount", style="bold")
            table.add_column("Payment status", style="bold")

            for index, taxe in enumerate(taxes, start=1):
                colums = taxe.split("&")
                amount, payment = self.payment_changes(colums[2], colums[3])
                table.add_row(str(index), colums[0], colums[1], amount, payment)

            self.update(table)

    async def fetch_date(self) -> None:
        taxes = cli.new_esse3_wrapper().fetch_taxes()
        await self.query_one("#taxes-loading").remove()
        self.query_one(Container).mount(
            Vertical(
                self.Tables(taxes),
            )
        )

    async def on_mount(self) -> None:
        await asyncio.sleep(0.1)
        asyncio.create_task(self.fetch_date())

    def compose(self) -> ComposeResult:
        yield Header("Taxes", classes="header")
        yield Container(
            Static("List of taxes", classes="title"),
            Static("[#ec971f]taxes loading[/] in progress.....", id="taxes-loading"),
        )
        yield Footer()

    BINDINGS = [
        Binding(key="r", action="app.pop_screen", description="return"),
        Binding(key="w", action="app.refresh('taxes')", description="refresh")
    ]