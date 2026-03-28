from fastapi import FastAPI
from routers import gameweek, players, optimize
from fastapi.middleware.cors import CORSMiddleware
from config import ALLOWED_ORIGINS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(gameweek.router)

app.include_router(players.router)

app.include_router(optimize.router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI"}

@app.get("/healthz")
def get_healtz():
    return {"status": "ok"}

#currently using cli no need. 
#if __name__ == "__main__":
    #uvicorn.run(app, host="HOST", port=PORT, reload=True)