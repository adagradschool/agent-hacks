from fastapi import FastAPI
from src.planner import generate_plan, PlannedProject
app = FastAPI()


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/plan")
async def plan(report: str) -> PlannedProject:
    plan = generate_plan(report)
    return plan