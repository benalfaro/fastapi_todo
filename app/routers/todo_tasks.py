from typing import Annotated

from fastapi import APIRouter, Body, HTTPException
from sqlmodel import func, select

from app.dependencies import SessionDep
from app.models.schemas import TodoDataResponse, TodoTaskCreate, TodoTaskPublic
from app.models.table_models import TodoTask

router = APIRouter(
    prefix="/todos",
    tags=["todo"],
)

@router.post("/", status_code=201)
def create_todo_item(
    task: Annotated[TodoTaskCreate, Body()], session: SessionDep) -> TodoTaskPublic:
    record = TodoTask.model_validate(task)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record

@router.get("")
def read_records(session: SessionDep) -> TodoDataResponse:
    data = session.exec(select(TodoTask)).all()
    record_count = session.exec(select(func.count()).select_from(TodoTask)).one()
    return {"data": data, "page": 1, "limit": 10, "total": record_count}

@router.get("/{record_id}")
def read_record(record_id: int, session:SessionDep) -> TodoTaskPublic:
    record = session.get(TodoTask, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No todo task with id {record_id} found")
    return record

@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, session: SessionDep):
    record = session.get(TodoTask, record_id)
    if record is None:
            raise HTTPException(status_code=404, detail=f"No todo task with id {record_id} found")
    session.delete(record)
    session.commit()

@router.put("/{record_id}")
def update_record(record_id: int, body: Annotated[TodoTaskCreate, Body()], session: SessionDep) -> TodoTaskPublic:
    record = session.get(TodoTask, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No todo task with id {record_id} found")    

    record.sqlmodel_update(body.model_dump())
    session.commit()
    session.refresh(record)
    return record
