from src.planner import generate_plan

def test_generate_plan():
    plan = generate_plan("I want to organize a birthday party for my friend on Saturday.")
    print(plan.model_dump_json(indent=2))
    assert plan is not None
    assert plan.project is not None
    assert plan.milestones is not None
    assert plan.labels is not None
    assert plan.issues is not None