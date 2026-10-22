from fastapi.testclient import TestClient
from http import HTTPStatus
from .main import app
from pydantic import BaseModel

from .main import TodoDataResponse, TodoTaskPublic, TodoTaskCreate 

client = TestClient(app)


def test_create_record():
    res = client.post("/todos", json={"title": "foo", "description": "bar"})
    assert TodoTaskPublic.model_validate(res.json(), strict=True)

def test_create_record_unprocessable_content():
    res = client.post("/todos", json={"title": 1,"description": "bar"})
    assert res.status_code == HTTPStatus.UNPROCESSABLE_CONTENT

def test_read_records():
    res = client.get("/todos")
    assert TodoDataResponse.model_validate(res.json(), strict=True)

def test_delete_record_not_found():
    res = client.delete("/todos/1")
    assert res.status_code == 404