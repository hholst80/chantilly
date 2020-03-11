import pickle
import os
import uuid

from creme import linear_model
from flask import g

from app import db
from app import cli


def test_set_model(app):
    runner = app.test_cli_runner()

    # Pickle a model
    model = linear_model.LinearRegression()
    probe = uuid.uuid4()
    model.probe = probe
    with open('tmp.pkl', 'wb') as f:
        pickle.dump(model, f)

    # Add the model to the shelf through the CLI
    result = runner.invoke(cli.set_model_command, ['tmp.pkl'])
    assert result.exit_code == 0

    # Check that the model has been added to the shelf
    with app.app_context():
        shelf = db.get_shelf()
        assert isinstance(shelf['model'], linear_model.LinearRegression)
        assert shelf['model'].probe == probe

    # Delete the pickle
    os.remove('tmp.pkl')
