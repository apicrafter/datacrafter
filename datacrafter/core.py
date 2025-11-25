#!/usr/bin/env python
# -*- coding: utf8 -*-
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Tuple, List

import typer
import yaml

from .cmds.project import Project
from .extractors.base import DataCrafterConfigurationError

# Configure default logging - INFO level for production use
# This can be overridden by enable_verbose() or quiet mode
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    force=False)  # Don't override if already configured

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
        with open(config_file, 'r', encoding='utf8') as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in configuration file: {e}")


@app.command()
def run(
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Verbose output. Print additional info on command execution'),
    path: Optional[str] = typer.Option(None, '--path', '-p', help='Project path. If not set, current directory used'),
    skip_validation: bool = typer.Option(False, '--skip-validation', help='Skip configuration validation before execution'),
    quiet: bool = typer.Option(False, '--quiet', '-q', help='Quiet mode. Only show errors'),
    structured_log: bool = typer.Option(False, '--structured-log', help='Use structured JSON logging')
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
                typer.echo(typer.style("Configuration validation failed:", fg=typer.colors.RED, bold=True))
                for error in errors:
                    typer.echo(f"  - {error}")
                typer.echo("\nRun 'datacrafter config validate' for detailed validation.")
                raise typer.Exit(1)
        except (FileNotFoundError, ValueError) as e:
            typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED))
            raise typer.Exit(1)
    
    try:
        project = Project(project_path)
        project.run(structured_log=structured_log)
    except DataCrafterConfigurationError as e:
        typer.echo(typer.style(f"Configuration error: {e}", fg=typer.colors.RED))
        typer.echo("Run 'datacrafter config validate' to check your configuration.")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED))
        if verbose:
            import traceback
            typer.echo(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def log(
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Verbose output. Print additional info on command execution'),
    path: Optional[str] = typer.Option(None, '--path', '-p', help='Project path. If not set, current directory used'),
    lines: int = typer.Option(50, '--lines', '-n', help='Number of lines to show')
):
    """Show log of latest operations"""
    if verbose:
        enable_verbose()
    
    project_path = get_project_path(path)
    log_file = os.path.join(project_path, 'datacrafter.log')
    
    if not os.path.exists(log_file):
        typer.echo(f"Log file not found: {log_file}")
        typer.echo("No operations have been logged yet.")
        return
    
    try:
        with open(log_file, 'r', encoding='utf8') as f:
            all_lines = f.readlines()
            # Show last N lines
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            typer.echo("".join(recent_lines))
    except Exception as e:
        typer.echo(typer.style(f"Error reading log file: {e}", fg=typer.colors.RED))
        raise typer.Exit(1)


@app.command()
def check(
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Verbose output. Print additional info on command execution'),
    path: Optional[str] = typer.Option(None, '--path', '-p', help='Project path. If not set, current directory used')
):
    """Validates configuration file and environment settings"""
    if verbose:
        enable_verbose()
    
    project_path = get_project_path(path)
    
    try:
        config = load_project_config(project_path)
        is_valid, errors = validate_config(config)
        
        if is_valid:
            typer.echo(typer.style("✓ Configuration is valid", fg=typer.colors.GREEN, bold=True))
            
            # Check environment
            env_issues = check_environment()
            if env_issues:
                typer.echo(typer.style("\nEnvironment issues:", fg=typer.colors.YELLOW))
                for issue in env_issues:
                    typer.echo(f"  - {issue}")
            else:
                typer.echo(typer.style("✓ Environment check passed", fg=typer.colors.GREEN))
        else:
            typer.echo(typer.style("✗ Configuration validation failed:", fg=typer.colors.RED, bold=True))
            for error in errors:
                typer.echo(f"  - {error}")
            raise typer.Exit(1)
    except (FileNotFoundError, ValueError) as e:
        typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED))
        raise typer.Exit(1)


def validate_config(config: dict) -> Tuple[bool, List[str]]:
    """Validate configuration and return (is_valid, errors)"""
    errors = []
    
    # Check required top-level keys
    required_keys = ['version', 'project-name', 'extractor']
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: '{key}'")
    
    # Validate extractor configuration
    if 'extractor' in config:
        extractor = config['extractor']
        if not isinstance(extractor, dict):
            errors.append("'extractor' must be a dictionary")
        else:
            required_extractor_keys = ['mode', 'type', 'method']
            for key in required_extractor_keys:
                if key not in extractor:
                    errors.append(f"Missing required extractor key: '{key}'")
    
    # Validate processor configuration if present
    if 'processor' in config:
        processor = config['processor']
        if not isinstance(processor, dict):
            errors.append("'processor' must be a dictionary")
    
    # Validate destination configuration if present
    if 'destination' in config:
        destination = config['destination']
        if not isinstance(destination, dict):
            errors.append("'destination' must be a dictionary")
        elif 'type' not in destination:
            errors.append("'destination' must have a 'type' key")
    
    return len(errors) == 0, errors


def check_environment() -> list[str]:
    """Check environment and return list of issues"""
    issues = []
    
    # Check if required directories exist
    # This is a basic check - more can be added
    
    return issues


@config_app.command("validate")
def config_validate(
    path: Optional[str] = typer.Option(None, '--path', '-p', help='Project path. If not set, current directory used'),
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
            typer.echo(typer.style("✓ Configuration is valid", fg=typer.colors.GREEN, bold=True))
        else:
            typer.echo(typer.style("✗ Configuration validation failed:", fg=typer.colors.RED, bold=True))
            for error in errors:
                typer.echo(f"  - {error}")
            raise typer.Exit(1)
    except (FileNotFoundError, ValueError) as e:
        typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED))
        raise typer.Exit(1)


@config_app.command("schema")
def config_schema():
    """Show expected configuration file schema"""
    schema_example = """# datacrafter.yml - Project Configuration Schema

version: "1"                    # Configuration version
project-name: "my-project"      # Project name
project-id: "unique-id"         # Unique project identifier (auto-generated)

extractor:
  mode: "singlefile"            # Extraction mode: singlefile, api, code
  type: "file-csv"              # Source type: file-csv, file-json, file-xml, api, code
  method: "url"                 # Method: url, urlbypattern, apibackuper
  force: true                   # Force re-download
  config:
    url: "https://example.com/data.csv"  # URL for url method
    # For urlbypattern:
    # prefix: "https://example.com/"
    # data_prefix: "data-"

processor:
  config:
    autoid: true                # Auto-generate IDs
    autotype: false            # Auto-detect types
    error_strategy: "skip"     # Error handling: skip, fail, retry
    max_retries: 3             # Max retries for failed records
  keymap:                      # Optional: field mapping
    type: "names"              # names or position
    fields:
      old_name: "new_name"
  typemap:                     # Optional: type conversion
    field_name: "int"          # int, float, date, datetime, bool
  custom:                      # Optional: custom code
    type: "script"
    code: "path/to/script.py"

destination:
  type: "file-jsonl"           # file-jsonl, file-csv, file-bson, mongodb, arangodb
  fileprefix: "output"         # Output file prefix
  compress: "gz"               # Optional: gz, bz2, xz, zip
  # For databases:
  # connstr: "mongodb://localhost:27017"
  # dbname: "mydb"
  # tablename: "mytable"
"""
    typer.echo(schema_example)


@app.command()
def init(
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Verbose output. Print additional info on command execution'),
    path: Optional[str] = typer.Option(None, '--path', '-p', help='Project path. If not set, current directory used'),
    name: Optional[str] = typer.Option(None, '--name', '-n', help='Project name. If not set, dummy name used')
):
    """Initialize project"""
    if verbose:
        enable_verbose()
    project = Project(path) if path else Project()
    project.init(name)
    typer.echo(typer.style("✓ Project initialized successfully", fg=typer.colors.GREEN))
    typer.echo(f"Run 'datacrafter config schema' to see configuration options.")


@app.command()
def clean(
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Verbose output. Print additional info on command execution'),
    path: Optional[str] = typer.Option(None, '--path', '-p', help='Project path. If not set, current directory used'),
    storage: bool = typer.Option(False, '--storage', help='Also clean storage directory')
):
    """Remove latest temporary files"""
    if verbose:
        enable_verbose()
    project = Project(path) if path else Project()
    project.clean(clean_storage=storage)
    typer.echo(typer.style("✓ Cleanup complete", fg=typer.colors.GREEN))


@app.command()
def status(
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Verbose output. Print additional info on command execution'),
    path: Optional[str] = typer.Option(None, '--path', '-p', help='Project path. If not set, current directory used')
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
        import json
        with open(state_file, 'r', encoding='utf8') as f:
            state = json.load(f)
        
        if 'stages' not in state or len(state['stages']) == 0:
            typer.echo("No execution stages found in state.")
            return
        
        typer.echo(typer.style("Pipeline Execution Status:", fg=typer.colors.CYAN, bold=True))
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
            
            typer.echo(f"{status_icon} Stage {i}: {stage_name} - {stage_status}")
            
            if 'results' in stage and stage['results']:
                if isinstance(stage['results'], list):
                    typer.echo(f"   Results: {len(stage['results'])} items")
                else:
                    typer.echo(f"   Results: {stage['results']}")
        
        # Show last stage status
        last_stage = state['stages'][-1]
        if last_stage.get('status') == 'success':
            typer.echo("")
            typer.echo(typer.style("✓ Pipeline completed successfully", fg=typer.colors.GREEN))
        elif last_stage.get('status') == 'fail':
            typer.echo("")
            typer.echo(typer.style("✗ Pipeline failed", fg=typer.colors.RED))
    except Exception as e:
        typer.echo(typer.style(f"Error reading state: {e}", fg=typer.colors.RED))
        if verbose:
            import traceback
            typer.echo(traceback.format_exc())


@app.command()
def ui(
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Verbose output. Print additional info on command execution')
):
    """Launch user interface (not yet)"""
    if verbose:
        enable_verbose()
    typer.echo(typer.style("UI command not yet implemented", fg=typer.colors.YELLOW))
    typer.echo("This feature is planned for a future release.")


@app.command()
def schema(
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Verbose output. Print additional info on command execution')
):
    """Generates and/or prints generated data schema (not yet)"""
    if verbose:
        enable_verbose()
    typer.echo(typer.style("Schema command not yet implemented", fg=typer.colors.YELLOW))
    typer.echo("This feature is planned for a future release.")


@app.command()
def builds(
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Verbose output. Print additional info on command execution')
):
    """Operations with builds. Subcommands: create, remove, list (not yet)"""
    if verbose:
        enable_verbose()
    typer.echo(typer.style("Builds command not yet implemented", fg=typer.colors.YELLOW))
    typer.echo("This feature is planned for a future release.")


@app.command()
def push(
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Verbose output. Print additional info on command execution')
):
    """Push collected data to the remote storage (not yet)"""
    if verbose:
        enable_verbose()
    typer.echo(typer.style("Push command not yet implemented", fg=typer.colors.YELLOW))
    typer.echo("This feature is planned for a future release.")


@app.command()
def version():
    """Show this tool version"""
    from datacrafter import __version__
    typer.echo(f'datacrafter version {__version__}')


@app.command()
def metrics(
    verbose: bool = typer.Option(False, '--verbose', '-v', help='Verbose output. Print additional info on command execution')
):
    """Metrics of the dataset (stats, datatypes, analysis results) (not yet)"""
    if verbose:
        enable_verbose()
    typer.echo(typer.style("Metrics command not yet implemented", fg=typer.colors.YELLOW))
    typer.echo("This feature is planned for a future release.")


def cli():
    """Main CLI entry point"""
    app()


if __name__ == '__main__':
    cli()
