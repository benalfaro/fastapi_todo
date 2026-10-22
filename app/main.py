import uvicorn
from typing import Annotated
from fastapi import FastAPI, Path
from dotenv import load_dotenv
import os
from fastapi.params import Body
from pydantic import BaseModel, Field
from fastapi.exceptions import HTTPException
from itertools import count

app = FastAPI()

load_dotenv()

_next_id = count(start=1)

db = {}



class TodoTaskCreate(BaseModel):
    title: str
    description: str
    
class TodoTaskPublic(BaseModel):
    id: int
    title: str
    description: str


class TodoDataResponse(BaseModel):
    data: list[TodoTaskPublic]
    page: int
    limit: int
    total: int


@app.post("/todos", status_code=201)
async def create_todo_item(
    task: Annotated[TodoTaskCreate, Body()],
) -> TodoTaskPublic:
    record_id = next(_next_id)
    record = TodoTaskPublic(id=record_id, **task.model_dump())
    record_dict = record.model_dump()
    db[record_id] = record_dict 
    return record

@app.get("/todos")
async def read_records() -> TodoDataResponse:
    return {"data": db.values(), "page": 1, "limit": 10, "total": len(db)}

@app.delete("/todos/{record_id}", status_code=204)
async def delete_record(record_id: int):
    if record_id in db.keys():
            raise HTTPException(status_code=404, detail=f"No todo task with id {record_id} found")
    db.pop(record_id)

@app.put("/todos/{record_id}")
async def update_item(record_id: int, body: Annotated[TodoTaskCreate, Body()]) -> TodoTaskPublic:
    if record_id not in db:
        raise HTTPException(status_code=404, detail=f"No todo task with id {record_id} found")
    
    task = TodoTaskPublic(id=record_id, **body.model_dump())
    db[record_id] = task.model_dump()
    return task

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
