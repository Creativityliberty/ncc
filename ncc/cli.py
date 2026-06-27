from __future__ import annotations

import json

import typer
from rich import print

from .runtime import NCCRuntime

app = typer.Typer(help="NCC-V0 local runtime", no_args_is_help=True)


@app.callback()
def main() -> None:
    """NCC-V0 command line interface."""
    return None


@app.command("demo")
def demo() -> None:
    """Run a minimal NCC-V0 demo."""
    runtime = NCCRuntime()
    trace = runtime.step("Chef, fais la première version locale pour Mac avec installation, tests, docs et interprétation des résultats.")
    print("[bold green]NCC-V0 demo executed.[/bold green]")
    print(json.dumps(trace.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
