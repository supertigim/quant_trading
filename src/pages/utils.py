from nicegui import ui


def check_auth():
    """Check if user is logged in, redirect to login page if not."""
    user = ui.local_storage.get("user")
    if not user:
        ui.open("/login")
        return False
    return True
