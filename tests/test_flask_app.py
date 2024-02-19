import os
import sys
import json
import pandas as pd
import pytest

print(os.getcwd())
sys.path.append(os.getcwd())
from src.flask_app import app, dataset, dataset_path

origin_length = len(dataset.to_dict(orient='records'))

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_get_route_1(client):
    target = dataset.to_dict(orient='records')
    response = client.get('/get_all_data')

    assert response.status_code == 200
    result_data = json.loads(response.data)

    assert set(result_data[0].keys()) == set(target[0].keys())

    for i in range(len(result_data)):
        for key in result_data[i].keys():
            assert result_data[i][key] == target[i][key]


def test_get_route_2(client):
    target = dataset.head(10).to_dict(orient='records')
    response = client.get('/get_all_data')

    assert response.status_code == 200
    result_data = json.loads(response.data)[0:10]

    assert set(result_data[0].keys()) == set(target[0].keys())

    for i in range(len(result_data)):
        for key in result_data[i].keys():
            assert result_data[i][key] == target[i][key]


def test_post_route_1(client):
    post_data = {"PUBUKPRN": 0, "UKPRN": 0, "KISCOURSEID": "100", "KISMODE": 200.0,
                 "EMPPOP": 300.0, "EMPRESPONSE": 400.0, "EMPSAMPLE": 500.0, "EMPRESP_RATE": 600.0,
                 "WORKSTUDY": 700.0, "STUDY": 800.0, "UNEMP": 800.0, "PREVWORKSTUD": 800.0,
                 "BOTH": 800.0, "NOAVAIL": 800.0, "WORK": 800.0}

    response = client.post('/post_new_data', json=post_data)

    assert response.status_code == 201
    result_data = json.loads(response.data)

    assert result_data == {'message': 'New data record added successfully'}

    dataset = pd.read_csv(dataset_path)
    new_data_record = pd.DataFrame([post_data])

    assert new_data_record.iloc[0].to_dict() == dataset.iloc[-1].to_dict()


def test_post_route_2(client):
    post_data = {"PUBUKPRN": 0, "UKPRN": 0, "KISCOURSEID": "100", "KISMODE": 200.0}

    response = client.post('/post_new_data', json=post_data)

    assert response.status_code == 400
    result_data = json.loads(response.data)

    assert result_data == {'error': 'Missing keys in the new data record'}


def test_put_route_1(client):
    put_data = {"PUBUKPRN": 0, "UKPRN": 0, "KISCOURSEID": "100", "KISMODE": 200.0,
                 "EMPPOP": 300.0, "EMPRESPONSE": 400.0, "EMPSAMPLE": 500.0, "EMPRESP_RATE": 600.0,
                 "WORKSTUDY": 700.0, "STUDY": 800.0, "UNEMP": 800.0, "PREVWORKSTUD": 800.0,
                 "BOTH": 800.0, "NOAVAIL": 800.0, "WORK": 850.0}

    response = client.put('/update_data/PUBUKPRN-0', json=put_data)

    assert response.status_code == 200
    result_data = json.loads(response.data)

    assert result_data == {'message': 'Data record updated successfully'}

    dataset = pd.read_csv(dataset_path)
    new_data_record = pd.DataFrame([put_data])

    assert new_data_record.iloc[0].to_dict() == dataset.iloc[-1].to_dict()


def test_put_route_2(client):
    put_data = {"PUBUKPRN": 0, "UKPRN": 0, "KISCOURSEID": "100", "KISMODE": 200.0,
                 "EMPPOP": 300.0, "EMPRESPONSE": 400.0, "EMPSAMPLE": 500.0, "EMPRESP_RATE": 600.0,
                 "WORKSTUDY": 700.0, "STUDY": 800.0, "UNEMP": 800.0, "PREVWORKSTUD": 800.0,
                 "BOTH": 800.0, "NOAVAIL": 800.0, "WORK": 850.0}

    response = client.put('/update_data/PUBUKPRN-1', json=put_data)

    assert response.status_code == 404
    result_data = json.loads(response.data)

    assert result_data == {'error': f'Data record with target_record_key 1 not found'}


def test_delete_route_1(client):
    response = client.delete('/delete_data/PUBUKPRN-0')

    assert response.status_code == 201
    result_data = json.loads(response.data)

    assert result_data == {'message': 'Data records deleted successfully'}

    dataset = pd.read_csv(dataset_path)

    assert dataset['PUBUKPRN'].isin([0]).any() == False


def test_delete_route_2(client):
    response = client.delete('/delete_data/PUBUKPRN-1')

    assert response.status_code == 201
    result_data = json.loads(response.data)

    assert result_data == {'message': 'Data records deleted successfully'}

    dataset = pd.read_csv(dataset_path)

    assert len(dataset) == origin_length