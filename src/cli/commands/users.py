import typer
import asyncio
from sqlalchemy import text
import uuid
from src.core.security import get_password_hash
from src.db.session import AsyncSessionLocal

app = typer.Typer()


@app.command()
def create_superuser(
    email: str = typer.Option(..., prompt=True),
    username: str = typer.Option(..., prompt=True),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, confirmation_prompt=True
    ),
):
    """Create a superuser account."""

    async def _create_superuser():
        async with AsyncSessionLocal() as db:
            # Check if user already exists
            result = await db.execute(
                text(
                    "SELECT * FROM users WHERE email = :email OR username = :username"
                ),
                {"email": email, "username": username},
            )
            existing_user = result.first()

            if existing_user:
                typer.echo("Error: User with this email or username already exists.")
                return

            # Create superuser
            hashed_password = get_password_hash(password)
            await db.execute(
                text(
                    """
                INSERT INTO users (
                    id, email, username, hashed_password, is_active, is_superuser,
                    created_at, updated_at
                )
                VALUES (
                    :id, :email, :username, :hashed_password, :is_active, :is_superuser,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
                """
                ),
                {
                    "id": str(uuid.uuid4()),
                    "email": email,
                    "username": username,
                    "hashed_password": hashed_password,
                    "is_active": True,
                    "is_superuser": True,
                },
            )
            await db.commit()
            typer.echo(f"Superuser {username} created successfully!")

    asyncio.run(_create_superuser())
