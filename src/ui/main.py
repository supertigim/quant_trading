from nicegui import ui


def create_main_page():
    with ui.card().classes("w-full max-w-2xl mx-auto mt-8"):
        ui.label("Welcome to Quant Trading").classes("text-2xl font-bold mb-4")

        # User info section
        with ui.card().classes("w-full mb-4"):
            ui.label("User Information").classes("text-xl font-semibold mb-2")

            user_info = ui.label("Loading...").classes("text-gray-600")

            async def load_user_info():
                user = ui.storage.user.get("user")
                if user and isinstance(user, dict):
                    username = user.get("username", "N/A")
                    email = user.get("email", "N/A")
                    user_id = user.get("id", "N/A")

                    user_info_text = f"Username: {username}\n"
                    if email != "N/A":
                        user_info_text += f"Email: {email}\n"
                    if user_id != "N/A":
                        user_info_text += f"User ID: {user_id}"

                    user_info.set_text(user_info_text.strip())

                    if email == "N/A" or user_id == "N/A":
                        ui.notify("Some user details might be missing.", type="warning")
                else:
                    user_info.set_text("User not logged in or user data is invalid.")

            load_user_info()

        # Logout button
        async def handle_logout():
            ui.storage.user.pop("token", None)
            ui.storage.user.pop("user", None)
            ui.notify("Logged out successfully", type="positive")
            ui.open("/login")

        ui.button("Logout", on_click=handle_logout).classes("bg-red-500 text-white")
