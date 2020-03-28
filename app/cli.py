import click
import contextlib
import dill
import flask
import os

from . import db


@click.command('init', short_help='set the flavor')
@click.argument('flavor')
def init(flavor):
    """Sets the flavor of chantilly.

    Calling this will reset the stored metrics.

    """
    db.set_flavor(flavor)


@click.command('add-model', short_help='add a model')
@click.argument('path', type=click.File('rb'))
@click.option('--name', type=str, default=None)
def add_model(path, name):
    """Stores a pickled/dilled model.

    A default name will be picked if none is given.

    """
    name = db.add_model(model=dill.load(path), name=name)
    click.echo(f'{name} has been added')


@click.command('delete-model', short_help='delete a model')
@click.argument('name', type=str)
def delete_model(name):
    db.delete_model(name)
    click.echo(f'{name} has been deleted')
