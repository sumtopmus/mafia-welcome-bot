from .debug import create_handlers as debug_handlers
from .info import create_handlers as info_handlers
from .admin import create_handlers as admin_handlers


def create_handlers() -> list:
    """Creates handlers that process admin's commands."""
    return debug_handlers() + info_handlers() + admin_handlers()