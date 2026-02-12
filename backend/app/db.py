import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()  # reads key/value pairs from .env into environment variables [web:119][web:126]

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite with a web server
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # session factory [web:145]

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db  # FastAPI can use dependencies that yield and then clean up after the response [web:138]
    finally:
        db.close()
