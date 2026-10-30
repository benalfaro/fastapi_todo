from .table_models import TodoTaskBase

from pydantic import BaseModel

class TodoTaskPublic(TodoTaskBase):
    id: int

class TodoTaskCreate(TodoTaskBase):
    pass

class TodoDataResponse(BaseModel):
    data: list[TodoTaskPublic]
    page: int
    limit: int
    total: int

class Token(BaseModel):
    value: str