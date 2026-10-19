import uvicorn
from typing import Annotated
from fastapi import FastAPI, Path
from dotenv import load_dotenv
import os
from fastapi.params import Body
from pydantic import BaseModel, Field
from fastapi.exceptions import HTTPException

app = FastAPI()

load_dotenv()

counter = 1

db = {}


class TodoRequestModel(BaseModel):
    title: str
    description: str


class TodoItemResponse(BaseModel):
    id: int
    title: str
    description: str


class TodoDataResponse(BaseModel):
    data: list[TodoItemResponse]
    page: int
    limit: int
    total: int


@app.post("/todos", status_code=201)
async def create_todo_item(
    item: Annotated[TodoRequestModel, Body()],
) -> TodoItemResponse:
    global counter
    item_dict = item.model_dump()
    item_dict.update({"id": counter})
    db[counter] = item_dict
    counter += 1
    return TodoItemResponse(**item_dict)


@app.get("/todos")
async def read_items() -> TodoDataResponse:
    return {"data": db, "page": 1, "limit": 10, "total": len(db)}

@app.delete("/todos/{item_id}", status_code=204)
async def delete_item(item_id: int):
    for index in range(0,len(db)):
        if db[index].id == item_id:
            raise HTTPException(status_code=404, detail="No todo item found for that user.")
        else:
            db.pop(index)
            break

@app.put("/todos/{item_id}")
async def update_item(item_id: int, body: Annotated[TodoRequestModel, Body()]) -> TodoItemResponse:
    for index,item in enumerate(db):
        if item.id == item_id:
            db[index] = body
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
