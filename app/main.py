from typing import Annotated
from fastapi import FastAPI
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv() 


@app.get("/")
async def root():
    return {"message": "Welcome to fastapi-todo-api!"}
