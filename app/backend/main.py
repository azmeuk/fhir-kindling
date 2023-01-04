import pathlib
from typing import Optional

from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, select
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.backend.api.api import api_router
from app.backend.db import engine


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

site_path = pathlib.Path(__file__).parent.parent / "frontend" / "dist"

app.mount("/app", StaticFiles(directory=site_path, html=True), name="site")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/heroes/")
def create_hero(hero: Hero):
    with Session(engine) as session:
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero


@app.get("/heroes/")
def read_heroes():
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        return heroes
