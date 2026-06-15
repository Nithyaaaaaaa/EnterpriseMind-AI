from fastapi import FastAPI

from routes import auth
from database.database import engine, Base
from models import user


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="EnterpriseMind AI",
    version="1.0.0"
)


app.include_router(auth.router)


@app.get("/")
def home():
    return {
        "project": "EnterpriseMind AI",
        "status": "running 🚀"
    }


@app.get("/health")
def health():
    return {
        "message": "Backend healthy"
    }