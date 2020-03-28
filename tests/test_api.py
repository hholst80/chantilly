import json
import pickle
import pytest
import uuid

from creme import linear_model
from creme import tree

from app import db
from app import exceptions


@pytest.fixture
def log_reg(client):
    client.post('/api/model', data=pickle.dumps(linear_model.LogisticRegression()))


def test_init(client, app):
    r = client.post('/api/init',
        data=json.dumps({'flavor': 'regression'}),
        content_type='application/json'
    )
    assert r.status_code == 201

    with app.app_context():
        assert db.get_shelf()['flavor'].name == 'regression'


def test_init_bad_flavor(client, app):
    r = client.post('/api/init',
        data=json.dumps({'flavor': 'zugzug'}),
        content_type='application/json'
    )
    assert r.status_code == 400
    assert r.json == {'message': "Allowed flavors are 'regression'."}


def test_model_correct(client, app):

    # Instantiate a model
    model = tree.DecisionTreeClassifier()
    probe = uuid.uuid4()
    model.probe = probe

    # Upload the model
    client.post('/api/model', data=pickle.dumps(model))

    # Check that the model has been added to the shelf
    with app.app_context():
        shelf = db.get_shelf()
        assert isinstance(shelf['model'], tree.DecisionTreeClassifier)
        assert shelf['model'].probe == probe

    # Check that the model can be retrieved via the API
    model = pickle.loads(client.get('/api/model').get_data())
    assert isinstance(model, tree.DecisionTreeClassifier)
    assert model.probe == probe


class ModelWithoutFit:
    def predict_one(self, x):
        return True

def test_model_without_fit(client, app):
    r = client.post('/api/model', data=pickle.dumps(ModelWithoutFit()))
    assert r.json == {'message': 'Model does not implement fit_one.'}


class ModelWithoutPredict:
    def fit_one(self, x, y):
        return self

def test_model_without_predict(client, app):
    r = client.post('/api/model', data=pickle.dumps(ModelWithoutPredict()))
    assert r.json == {'message': 'Model does not implement predict_one or predict_proba_one.'}


def test_predict(client, app, log_reg):
    r = client.post('/api/predict',
        data=json.dumps({'features': {}}),
        content_type='application/json'
    )
    assert r.status_code == 200
    assert 'prediction' in r.json


def test_predict_no_model(client, app):
    r = client.post('/api/predict',
        data=json.dumps({'features': {}}),
        content_type='application/json'
    )
    assert r.json == {'message': 'You first need to provide a model.'}


def test_learn_no_model(client, app):
    r = client.post('/api/learn',
        data=json.dumps({'features': {'x': 1}, 'ground_truth': True}),
        content_type='application/json'
    )
    assert r.json == {'message': 'You first need to provide a model.'}


def test_predict_with_id(client, app, log_reg):

    r = client.post('/api/predict',
        data=json.dumps({'features': {}, 'id': '90210'}),
        content_type='application/json'
    )
    assert r.status_code == 201
    assert 'prediction' in r.json

    with app.app_context():
        shelf = db.get_shelf()
        assert '#90210' in shelf


def test_predict_no_features(client, app, log_reg):
    r = client.post('/api/predict',
        data=json.dumps({'id': 42}),
        content_type='application/json'
    )
    assert r.json == {'message': {'features': ['Missing data for required field.']}}


def test_learn(client, app, log_reg):
    r = client.post('/api/learn',
        data=json.dumps({'features': {'x': 1}, 'ground_truth': True}),
        content_type='application/json'
    )
    assert r.status_code == 201


def test_learn_with_id(client, app, log_reg):

    client.post('/api/predict',
        data=json.dumps({'id': 42, 'features': {'x': 1}}),
        content_type='application/json'
    )

    # Check the sample has been stored
    with app.app_context():
        shelf = db.get_shelf()
        assert shelf['#42']['features'] == {'x': 1}

    r = client.post('/api/learn',
        data=json.dumps({'id': 42, 'ground_truth': True}),
        content_type='application/json'
    )
    assert r.status_code == 201

    # Check the sample has now been removed
    with app.app_context():
        shelf = db.get_shelf()
        assert '#42' not in shelf


def test_learn_no_ground_truth(client, app, log_reg):
    r = client.post('/api/learn',
        data=json.dumps({'features': {'x': 1}}),
        content_type='application/json'
    )
    assert r.json == {'message': {'ground_truth': ['Missing data for required field.']}}


def test_learn_no_features(client, app, log_reg):
    r = client.post('/api/learn',
        data=json.dumps({'ground_truth': True}),
        content_type='application/json'
    )
    assert r.json == {'message': 'No features are stored and none were provided.'}
