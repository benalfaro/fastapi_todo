from fastapi import Depends
from typing import Annotated
from sqlmodel import Session, create_engine, SQLModel
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

DB_DIR = Path("data")
sqlite_db_url = os.getenv("SQLITE_URL")

connect_args = {"check_same_thread": False}
try:
    engine = create_engine(sqlite_db_url, connect_args=connect_args)
except Exception:
    raise

def create_database_and_tables():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
        
SessionDep = Annotated[Session, Depends(get_session)]

