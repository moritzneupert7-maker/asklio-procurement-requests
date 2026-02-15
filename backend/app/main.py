from fastapi import FastAPI

from .seed_commodity_groups import init_db
from .routers import requests, commodity_groups, chat

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="askLio Procurement Requests")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(requests.router)
app.include_router(commodity_groups.router)
app.include_router(chat.router)
