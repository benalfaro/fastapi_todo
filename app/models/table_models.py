from sqlmodel import Field, SQLModel
from pydantic import EmailStr

class TodoTaskBase(SQLModel):
    title: str
    description: str

class TodoTask(TodoTaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class UserBase(SQLModel):
    name: str = Field(min_length=1)
    email: EmailStr

class UserInDB(UserBase, table=True):
    password: str

