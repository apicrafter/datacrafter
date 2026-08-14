#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Core CLI module for datacrafter."""
import logging
import os
from typing import Optional

import typer
import yaml

from .cmds.project import Project, load_config
from .common.logconfig import configure_logging
from .common.validation import check_environment, validate_config
from .destinations import list_destinations
from .extractors import list_extractors
from .extractors.base import DataCrafterConfigurationError
from .sources import list_sources

# Default logging for `python -m datacrafter` and library imports.
# Project.enable_logging() replaces handlers when a pipeline actually runs.
configure_logging(logging.INFO)

# Create Typer app
app = typer.Typer(
    name="datacrafter",
    help="Datacrafter - NoSQL ETL tool",
    add_completion=False
)

# Create config subcommand group
config_app = typer.Typer(help="Configuration management commands")
app.add_typer(config_app, name="config")


def enable_verbose():
    """Enable verbose logging"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    # Update all existing handlers to DEBUG level
    for handler in root_logger.handlers:
        handler.setLevel(logging.DEBUG)


def get_project_path(path: Optional[str]) -> str:
    """Get project path, defaulting to current directory"""
    return path if path else os.getcwd()


def load_project_config(project_path: str) -> dict:
    """Load and return project configuration"""
    config_file = os.path.join(project_path, 'datacrafter.yml')
    if not os.path.exists(config_file):
        raise FileNotFoundError(
            f"Project configuration file not found: {config_file}\n"
            f"Run 'datacrafter init' to create a new project."
        )

    try:
        return load_config(config_file) or {}
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid YAML in configuration file: {error}") from error


@app.command()
def run(
    verbose: bool = typer.Option(
        False, '--verbose', '-v',
        help='Verbose output. Print additional info on command execution'),
    path: Optional[str] = typer.Option(
        None, '--path', '-p',
        help='Project path. If not set, current directory used'),
    skip_validation: bool = typer.Option(
        False, '--skip-validation',
        help='Skip configuration validation before execution'),
    quiet: bool = typer.Option(
        False, '--quiet', '-q', help='Quiet mode. Only show errors'),
    structured_log: bool = typer.Option(
        False, '--structured-log', help='Use structured JSON logging'),
    dry_run: bool = typer.Option(
        False, '--dry-run', help='Validate and print a plan; do not extract or write')
):
    """Execute data pipeline"""
    if quiet:
        # Set logging to ERROR level only
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.ERROR)
        for handler in root_logger.handlers:
            handler.setLevel(logging.ERROR)
    elif verbose:
        enable_verbose()

    project_path = get_project_path(path)

    # Validate configuration before execution
    if not skip_validation:
        try:
            config = load_project_config(project_path)
            is_valid, errors = validate_config(config)
            if not is_valid:
                typer.echo(typer.style(
                    "Configuration validation failed:",
                    fg=typer.colors.RED, bold=True))
                for error in errors:
                    typer.echo(f"  - {error}")
                typer.echo(
                    "\nRun 'datacrafter config validate' "
                    "for detailed validation.")
                raise typer.Exit(1)
        except (FileNotFoundError, ValueError) as error:
            typer.echo(typer.style(f"Error: {error}", fg=typer.colors.RED))
            raise typer.Exit(1)

    try:
        project = Project(project_path)
        if dry_run:
            plan = project.run(structured_log=structured_log, dry_run=True)
            typer.echo(yaml.safe_dump(plan, sort_keys=False))
            return
        project.run(structured_log=structured_log)
    except DataCrafterConfigurationError as error:
        typer.echo(typer.style(
            f"Configuration error: {error}", fg=typer.colors.RED))
        typer.echo(
            "Run 'datacrafter config validate' "
            "to check your configuration.")
        raise typer.Exit(1)
    except Exception as error:
        typer.echo(typer.style(f"Error: {error}", fg=typer.colors.RED))
        if verbose:
            import traceback  # pylint: disable=import-outside-toplevel
            typer.echo(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def log(
    verbose: bool = typer.Option(
        False, '--verbose', '-v',
        help='Verbose output. Print additional info on command execution'),
    path: Optional[str] = typer.Option(
        None, '--path', '-p',
        help='Project path. If not set, current directory used'),
    lines: int = typer.Option(
        50, '--lines', '-n', help='Number of lines to show')
):
    """Show log of latest operations"""
    if verbose:
        enable_verbose()

    project = Project(get_project_path(path))
    try:
        text = project.log(lines=lines)
    except OSError as error:
        typer.echo(typer.style(f"Error reading log file: {error}", fg=typer.colors.RED))
        raise typer.Exit(1)
    if text is None:
        typer.echo(f"Log file not found: {project.logfile}")
        typer.echo("No operations have been logged yet.")
        return
    typer.echo(text, nl=False)


@app.command()
def check(
    verbose: bool = typer.Option(
        False, '--verbose', '-v',
        help='Verbose output. Print additional info on command execution'),
    path: Optional[str] = typer.Option(
        None, '--path', '-p',
        help='Project path. If not set, current directory used')
):
    """Validates configuration file and environment settings"""
    if verbose:
        enable_verbose()

    project_path = get_project_path(path)

    try:
        config = load_project_config(project_path)
        is_valid, errors = validate_config(config)

        if is_valid:
            typer.echo(typer.style(
                "✓ Configuration is valid",
                fg=typer.colors.GREEN, bold=True))

            # Check environment
            env_issues = check_environment(config, project_path)
            if env_issues:
                typer.echo(typer.style(
                    "\nEnvironment issues:", fg=typer.colors.YELLOW))
                for issue in env_issues:
                    typer.echo(f"  - {issue}")
            else:
                typer.echo(typer.style(
                    "✓ Environment check passed", fg=typer.colors.GREEN))
        else:
            typer.echo(typer.style(
                "✗ Configuration validation failed:",
                fg=typer.colors.RED, bold=True))
            for error in errors:
                typer.echo(f"  - {error}")
            raise typer.Exit(1)
    except (FileNotFoundError, ValueError) as error:
        typer.echo(typer.style(f"Error: {error}", fg=typer.colors.RED))
        raise typer.Exit(1)


@config_app.command("validate")
def config_validate(
    path: Optional[str] = typer.Option(
        None, '--path', '-p',
        help='Project path. If not set, current directory used'),
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Verbose output')
):
    """Validate project configuration file"""
    if verbose:
        enable_verbose()

    project_path = get_project_path(path)

    try:
        config = load_project_config(project_path)
        is_valid, errors = validate_config(config)

        if is_valid:
            typer.echo(typer.style(
                "✓ Configuration is valid",
                fg=typer.colors.GREEN, bold=True))
        else:
            typer.echo(typer.style(
                "✗ Configuration validation failed:",
                fg=typer.colors.RED, bold=True))
            for error in errors:
                typer.echo(f"  - {error}")
            raise typer.Exit(1)
    except (FileNotFoundError, ValueError) as error:
        typer.echo(typer.style(f"Error: {error}", fg=typer.colors.RED))
        raise typer.Exit(1)


@config_app.command("schema")
def config_schema():
    """Show expected configuration file schema"""
    extractor_types = ', '.join(list_extractors())
    source_types = ', '.join(list_sources())
    dest_types = ', '.join(list_destinations())
    schema_example = f"""# datacrafter.yml - Project Configuration Schema

version: "1"                    # Configuration version
project-name: "my-project"      # Project name
project-id: "unique-id"         # Unique project identifier (auto-generated)

extractor:
  mode: "singlefile"            # singlefile, api, code
  type: "file-csv"              # {extractor_types}
  method: "url"                 # url, urlbypattern, apibackuper
  force: true                   # Force re-download
  config:
    url: "https://example.com/data.csv"  # URL for url method
    # For urlbypattern:
    # prefix: "https://example.com/"
    # data_prefix: "data-"
    # For type: code (script must live under the project directory):
    # script: "scripts/collect.py"

# Or several extractors sharing one processor/destination:
# extractors:
#   - name: csv
#     mode: singlefile
#     type: file-csv
#     method: url
#     config:
#       url: "https://example.com/a.csv"
#   - name: feed
#     type: rss
#     config:
#       url: "https://example.com/feed.xml"

processor:
  config:
    # autoid / autotype are applied when true (autoid default is false)
    autoid: true
    autotype: false
    error_strategy: "skip"     # skip, fail, retry
    max_retries: 3
    type: "csv"                # Optional reader type: {source_types}
  keymap:                      # Optional: field mapping
    type: "names"              # names or position
    fields:
      old_name: "new_name"
  typemap:                     # Optional: type conversion
    field_name: "int"          # int, float, date, datetime, bool
  custom:                      # Optional: custom code under the project dir
    type: "script"
    code: "scripts/transform.py"

destination:
  type: "file-jsonl"           # {dest_types}
  fileprefix: "output"         # Required for file-* destinations
  compress: "gz"               # Optional: gz, bz2, xz, zip, zst
  # For databases / search:
  # connstr: "mongodb://localhost:27017"
  # dbname: "mydb"
  # tablename: "mytable"
"""
    typer.echo(schema_example)


@app.command()
def init(
    directory: Optional[str] = typer.Argument(
        None,
        help='Project directory to create or initialize. Default: current directory'),
    verbose: bool = typer.Option(
        False, '--verbose', '-v',
        help='Verbose output. Print additional info on command execution'),
    path: Optional[str] = typer.Option(
        None, '--path', '-p',
        help='Project path. Alternative to DIRECTORY'),
    name: Optional[str] = typer.Option(
        None, '--name', '-n',
        help='Project name. Defaults to the directory name')
):
    """Initialize project"""
    if verbose:
        enable_verbose()
    if directory and path:
        typer.echo(typer.style(
            "Error: pass either a directory argument or --path, not both",
            fg=typer.colors.RED))
        raise typer.Exit(1)
    project_path = directory or path
    if name is None and project_path:
        name = os.path.basename(os.path.abspath(project_path))
    project = Project(project_path) if project_path else Project()
    project.init(name)
    typer.echo(typer.style(
        "✓ Project initialized successfully", fg=typer.colors.GREEN))
    typer.echo(
        "Edit datacrafter.yml to add an extractor (and optional processor/"
        "destination), then run 'datacrafter check'.")
    typer.echo(
        "Run 'datacrafter config schema' to see configuration options.")


@app.command()
def clean(
    verbose: bool = typer.Option(
        False, '--verbose', '-v',
        help='Verbose output. Print additional info on command execution'),
    path: Optional[str] = typer.Option(
        None, '--path', '-p',
        help='Project path. If not set, current directory used'),
    storage: bool = typer.Option(
        False, '--storage', help='Also clean storage directory')
):
    """Remove latest temporary files"""
    if verbose:
        enable_verbose()
    project = Project(path) if path else Project()
    project.clean(clean_storage=storage)
    typer.echo(typer.style("✓ Cleanup complete", fg=typer.colors.GREEN))


@app.command()
def status(
    verbose: bool = typer.Option(
        False, '--verbose', '-v',
        help='Verbose output. Print additional info on command execution'),
    path: Optional[str] = typer.Option(
        None, '--path', '-p',
        help='Project path. If not set, current directory used')
):
    """Status of latest data pipeline execution"""
    if verbose:
        enable_verbose()

    project_path = get_project_path(path)
    state_file = os.path.join(project_path, 'state.json')

    if not os.path.exists(state_file):
        typer.echo("No execution state found. Run 'datacrafter run' first.")
        return

    try:
        import json  # pylint: disable=import-outside-toplevel
        with open(state_file, 'r', encoding='utf8') as file_obj:
            state = json.load(file_obj)

        if 'stages' not in state or len(state['stages']) == 0:
            typer.echo("No execution stages found in state.")
            return

        typer.echo(typer.style(
            "Pipeline Execution Status:", fg=typer.colors.CYAN, bold=True))
        typer.echo("")

        for i, stage in enumerate(state['stages'], 1):
            stage_name = stage.get('name', 'unknown')
            stage_status = stage.get('status', 'unknown')

            if stage_status == 'success':
                status_icon = typer.style("✓", fg=typer.colors.GREEN)
            elif stage_status == 'fail':
                status_icon = typer.style("✗", fg=typer.colors.RED)
            else:
                status_icon = typer.style("?", fg=typer.colors.YELLOW)

            typer.echo(
                f"{status_icon} Stage {i}: {stage_name} - {stage_status}")

            if 'results' in stage and stage['results']:
                if isinstance(stage['results'], list):
                    typer.echo(f"   Results: {len(stage['results'])} items")
                else:
                    typer.echo(f"   Results: {stage['results']}")

        # Show last stage status
        last_stage = state['stages'][-1]
        if last_stage.get('status') == 'success':
            typer.echo("")
            typer.echo(typer.style(
                "✓ Pipeline completed successfully",
                fg=typer.colors.GREEN))
        elif last_stage.get('status') == 'fail':
            typer.echo("")
            typer.echo(typer.style(
                "✗ Pipeline failed", fg=typer.colors.RED))
    except Exception as error:
        typer.echo(typer.style(
            f"Error reading state: {error}", fg=typer.colors.RED))
        if verbose:
            import traceback
            typer.echo(traceback.format_exc())


@app.command()
def ui(
    verbose: bool = typer.Option(
        False, '--verbose', '-v',
        help='Verbose output. Print additional info on command execution')
):
    """Launch user interface (not yet)"""
    if verbose:
        enable_verbose()
    typer.echo(typer.style(
        "UI command not yet implemented", fg=typer.colors.YELLOW))
    typer.echo("This feature is planned for a future release.")


@app.command()
def schema(
    path: Optional[str] = typer.Option(
        None, '--path', '-p',
        help='Project path. If not set, current directory used')
):
    """Print inferred field types from project JSONL output."""
    from .common.infer import analyze_records, iter_jsonl_path, project_jsonl_files

    project_path = get_project_path(path)
    files = project_jsonl_files(project_path)
    if not files:
        typer.echo(
            "No JSONL files found in output/ or current/. "
            "Run the pipeline first.")
        raise typer.Exit(1)

    def records():
        for filename in files:
            yield from iter_jsonl_path(filename)

    field_types, _metrics = analyze_records(records())
    typer.echo(yaml.safe_dump({
        'files': files,
        'fields': field_types,
    }, sort_keys=False))


@app.command()
def metrics(
    path: Optional[str] = typer.Option(
        None, '--path', '-p',
        help='Project path. If not set, current directory used')
):
    """Print record counts and field histograms from project JSONL output."""
    from .common.infer import analyze_records, iter_jsonl_path, project_jsonl_files

    project_path = get_project_path(path)
    files = project_jsonl_files(project_path)
    if not files:
        typer.echo(
            "No JSONL files found in output/ or current/. "
            "Run the pipeline first.")
        raise typer.Exit(1)

    def records():
        for filename in files:
            yield from iter_jsonl_path(filename)

    _types, report = analyze_records(records())
    report['files'] = files
    typer.echo(yaml.safe_dump(report, sort_keys=False))


@app.command()
def builds(
    verbose: bool = typer.Option(
        False, '--verbose', '-v',
        help='Verbose output. Print additional info on command execution')
):
    """Operations with builds. Subcommands: create, remove, list (not yet)"""
    if verbose:
        enable_verbose()
    typer.echo(typer.style(
        "Builds command not yet implemented", fg=typer.colors.YELLOW))
    typer.echo("This feature is planned for a future release.")


@app.command()
def push(
    verbose: bool = typer.Option(
        False, '--verbose', '-v',
        help='Verbose output. Print additional info on command execution')
):
    """Push collected data to the remote storage (not yet)"""
    if verbose:
        enable_verbose()
    typer.echo(typer.style("Push command not yet implemented", fg=typer.colors.YELLOW))
    typer.echo("This feature is planned for a future release.")


@app.command()
def version():
    """Show this tool version"""
    from datacrafter import __version__  # pylint: disable=import-outside-toplevel
    typer.echo(f'datacrafter version {__version__}')


def cli():
    """Main CLI entry point"""
    app()


if __name__ == '__main__':
    cli()
