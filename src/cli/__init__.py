import typer
from src.cli.commands import users_app

app = typer.Typer()
app.add_typer(users_app, name="users", help="User management commands")
