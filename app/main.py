import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from app.routers import todo_tasks, auth
from app.dependencies import create_database_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

load_dotenv()

app.include_router(auth.router)
app.include_router(todo_tasks.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)