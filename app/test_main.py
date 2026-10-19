from fastapi.testclient import TestClient
from http import HTTPStatus
from .main import app
from pydantic import BaseModel

from .main import TodoDataResponse, TodoItemResponse, TodoRequestModel

client = TestClient(app)


def test_create_item():
    res = client.post("/todos", json={"title": "foo", "description": "bar"})
    assert TodoItemResponse.model_validate(res.json(), strict=True)

def test_create_item_unprocessable_content():
    res = client.post("/todos", json={"title": 1,"description": "bar"})
    assert res.status_code == HTTPStatus.UNPROCESSABLE_CONTENT

def test_read_items():
    res = client.get("/todos")
    assert TodoDataResponse.model_validate(res.json(), strict=True)
