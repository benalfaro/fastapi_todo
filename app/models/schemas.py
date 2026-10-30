from .table_models import TodoTaskBase, UserBase
from sqlmodel import Field
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


class UserRequest(UserBase):
    password: str = Field(min_length=10)


class Token(BaseModel):
    access_token: str