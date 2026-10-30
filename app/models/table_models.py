from sqlmodel import Field, SQLModel
from pydantic import EmailStr


class TodoTaskBase(SQLModel):
    title: str
    description: str


class TodoTask(TodoTaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True)
    name: str


class UserInDB(UserBase, table=True):
    id: int = Field(primary_key=True)
    password: str


