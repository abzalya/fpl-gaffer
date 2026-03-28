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


## what to do so far. 
# 01-db run main.py
# 02-dbt cd 02-dbt dbt run
# 03-ml run main.py to train & run predict.py to make predictions
# 04-optimizer run main_runner.py if manual but api wired up
# 05-api run server using cd 05-api & uvicorn main:app --reload