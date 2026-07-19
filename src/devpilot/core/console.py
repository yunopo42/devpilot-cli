"""Central Rich console instances used by DevPilot."""

from rich.console import Console

console = Console()
error_console = Console(stderr=True)
