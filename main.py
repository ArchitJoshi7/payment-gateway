from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db import engine, SessionLocal
from models import User, Base
from api import router as api_router

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.on_event("startup")
def on_startup():
    """Drop and recreate all tables, seed Alice with $1000, clear in-memory state."""
    # Reset database
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.add(User(name="Alice", balance=1000.0))
    db.commit()
    db.close()

    # Clear idempotency store so duplicate-key state doesn't carry over
    from idempotency import idempotency_store
    idempotency_store.clear()

    # Clear the in-memory event log
    app.state.log = []


app.include_router(api_router)
