from collections.abc import Iterator
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.dependencies import get_session
from app.main import app
from app.models.schemas import TodoDataResponse, TodoTaskPublic


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    previous_override = app.dependency_overrides.get(get_session)
    app.dependency_overrides[get_session] = override_get_session
    try:
        yield TestClient(app)
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_session, None)
        else:
            app.dependency_overrides[get_session] = previous_override
        engine.dispose()


def create_task(client: TestClient, title: str, description: str) -> TodoTaskPublic:
    response = client.post(
        "/todos/",
        json={"title": title, "description": description},
    )
    assert response.status_code == HTTPStatus.CREATED
    return TodoTaskPublic.model_validate(response.json())


def test_list_todos_returns_empty_collection(client: TestClient) -> None:
    response = client.get("/todos/")

    assert response.status_code == HTTPStatus.OK
    data = TodoDataResponse.model_validate(response.json())
    assert data.data == []
    assert data.page == 1
    assert data.limit == 10
    assert data.total == 0


def test_create_todo_returns_created_task(client: TestClient) -> None:
    response = client.post(
        "/todos/",
        json={"title": "Buy groceries", "description": "Milk and bread"},
    )

    assert response.status_code == HTTPStatus.CREATED
    task = TodoTaskPublic.model_validate(response.json())
    assert task.id > 0
    assert task.title == "Buy groceries"
    assert task.description == "Milk and bread"


@pytest.mark.parametrize(
    "payload",
    [
        {"description": "No title"},
        {"title": "No description"},
        {"title": 123, "description": "Invalid title type"},
    ],
)
def test_create_todo_rejects_invalid_payload(
    client: TestClient, payload: dict
) -> None:
    response = client.post("/todos/", json=payload)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_CONTENT


def test_list_todos_returns_created_tasks(client: TestClient) -> None:
    created = create_task(client, "Write tests", "Cover the todo endpoints")

    response = client.get("/todos/")

    assert response.status_code == HTTPStatus.OK
    data = TodoDataResponse.model_validate(response.json())
    assert data.total == 1
    assert len(data.data) == 1
    assert data.data[0].id == created.id
    assert data.data[0].title == "Write tests"
    assert data.data[0].description == "Cover the todo endpoints"


def test_get_todo_returns_task(client: TestClient) -> None:
    created = create_task(client, "Read", "Read a book")

    response = client.get(f"/todos/{created.id}")

    assert response.status_code == HTTPStatus.OK
    task = TodoTaskPublic.model_validate(response.json())
    assert task.id == created.id
    assert task.title == "Read"
    assert task.description == "Read a book"


def test_get_missing_todo_returns_not_found(client: TestClient) -> None:
    response = client.get("/todos/999")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "No todo task with id 999 found"}


def test_update_todo_replaces_task_fields(client: TestClient) -> None:
    created = create_task(client, "Old title", "Old description")

    response = client.put(
        f"/todos/{created.id}",
        json={"title": "New title", "description": "New description"},
    )

    assert response.status_code == HTTPStatus.OK
    task = TodoTaskPublic.model_validate(response.json())
    assert task.id == created.id
    assert task.title == "New title"
    assert task.description == "New description"


def test_update_missing_todo_returns_not_found(client: TestClient) -> None:
    response = client.put(
        "/todos/999",
        json={"title": "New title", "description": "New description"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "No todo task with id 999 found"}


def test_delete_todo_removes_task(client: TestClient) -> None:
    created = create_task(client, "Delete me", "This task should be removed")

    response = client.delete(f"/todos/{created.id}")

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b""
    assert client.get(f"/todos/{created.id}").status_code == HTTPStatus.NOT_FOUND


def test_delete_missing_todo_returns_not_found(client: TestClient) -> None:
    response = client.delete("/todos/999")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "No todo task with id 999 found"}
