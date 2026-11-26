from pathlib import Path
import typer
from .core import analyze, markdown
from .support import render_json
app = typer.Typer(help='Inspect log evidence and incident timelines.', add_completion=False)
@app.command()
def inspect(path: Path, question: str = '', ai: bool = False, json: bool = False):
    """Read a UTF-8 log. --ai sends redacted selected lines to the configured model."""
    try:
        report = analyze(path, question, ai)
        typer.echo(render_json(report) if json else markdown(report))
    except (ValueError, OSError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1)
