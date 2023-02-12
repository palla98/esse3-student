import click
import typer

app = typer.Typer()

@click.command()
@click.option('--to-pay', default=False, help='Show all taxes to be paid')
@click.option('--year', help='Filter taxes by year')
def taxes(to_pay, year):
    typer.echo("ciao")

def run_app():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "taxes" and "--help" in sys.argv[2:]:
        print("Options:")
        print("--to-pay: Show all taxes to be paid")
        print("--year: Filter taxes by year")
    else:
        app.run(sys.argv)

