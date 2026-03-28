from fastapi import FastAPI
from routers import gameweek, players, optimize

app = FastAPI()

app.include_router(gameweek.router)

app.include_router(players.router)

app.include_router(optimize.router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI"}

@app.get("/healthz")
def get_healtz():
    return {"status": "ok"}

# FastAPI app, CORS, Config
