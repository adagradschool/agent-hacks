from fastapi import FastAPI
from src.planner import generate_plan, PlannedProject
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/plan/{report}")
async def plan(report: str) -> PlannedProject:
    plan = generate_plan(report)
    return plan