#!/usr/bin/env python
# -*- coding: utf8 -*-
import click
import logging

from .cmds.project import Project

#logging.getLogger().addHandler(logging.StreamHandler())
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)

def enableVerbose():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)


@click.group()
def cli1():
    pass

@cli1.command()
@click.option('--verbose', '-v', count=True, help='Verbose output. Print additional info on command execution')
def run(verbose):
    """Execute data pipeline"""
    if verbose:
        enableVerbose()
    project = Project()
    project.run()
    pass


@click.group()
def cli2():
    pass

@cli2.command()
@click.option('--verbose', '-v', count=True, help='Verbose output. Print additional info on command execution')
def log(verbose):
    """Show log of latest operations (not yet)"""
    if verbose:
        enableVerbose()
    pass

@click.group()
def cli3():
    pass

@cli3.command()
@click.option('--verbose', '-v', count=True, help='Verbose output. Print additional info on command execution')
def check(verbose):
    """Validates configuration file and environment settings (not yet)"""
    if verbose:
        enableVerbose()
    pass

@click.group()
def cli4():
    pass

@cli4.command()
@click.option('--verbose', '-v', count=True, help='Verbose output. Print additional info on command execution')
def init(verbose):
    """Initialize project (not yet)"""
    if verbose:
        enableVerbose()
    pass

@click.group()
def cli5():
    pass

@cli5.command()
@click.option('--verbose', '-v', count=True, help='Verbose output. Print additional info on command execution')
def clean(verbose):
    """Remove latest temporary files"""
    if verbose:
        enableVerbose()
    project = Project()
    project.clean()
    pass

@click.group()
def cli6():
    pass

@cli6.command()
@click.option('--verbose', '-v', count=True, help='Verbose output. Print additional info on command execution')
def ui(verbose):
    """Launch user interface (not yet)"""
    if verbose:
        enableVerbose()
    pass

@click.group()
def cli7():
    pass

@cli7.command()
@click.option('--verbose', '-v', count=True, help='Verbose output. Print additional info on command execution')
def schema(verbose):
    """Generates and/or prints generated data schema (not yet)"""
    if verbose:
        enableVerbose()
    pass

@click.group()
def cli8():
    pass

@cli8.command()
@click.option('--verbose', '-v', count=True, help='Verbose output. Print additional info on command execution')
def builds(verbose):
    """Operations with builds. Subcommands: create, remove, list (not yet)"""
    if verbose:
        enableVerbose()
    pass

@click.group()
def cli9():
    pass

@cli9.command()
@click.option('--verbose', '-v', count=True, help='Verbose output. Print additional info on command execution')
def push(verbose):
    """Push collected data to the remote storage (not yet)"""
    if verbose:
        enableVerbose()
    pass

@click.group()
def cli10():
    pass

@cli10.command()
def version():
    """This tool version"""
    from datacrafter import __version__
    print('datacrafter version %s' % (__version__))


@click.group()
def cli11():
    pass

@cli11.command()
@click.option('--verbose', '-v', count=True, help='Verbose output. Print additional info on command execution')
def metrics(verbose):
    """Metrics of the dataset (stats, datatypes, analysis results) (not yet)"""
    if verbose:
        enableVerbose()
    pass

@click.group()
def cli12():
    pass

@cli12.command()
@click.option('--verbose', '-v', count=True, help='Verbose output. Print additional info on command execution')
def status(verbose):
    """Status of latest data pipeline execution (not yet)"""
    if verbose:
        enableVerbose()
    pass



cli = click.CommandCollection(sources=[cli1, cli2, cli3, cli4, cli5, cli6, cli7, cli8, cli9, cli10, cli11, cli12])

#if __name__ == '__main__':
#    cli()

