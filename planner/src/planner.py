from openai import OpenAI
from pydantic import BaseModel
from src.schemas import Plan
from src.config import config
from src.linear import Linear, LinearMilestone, LinearLabel, LinearProject

client = OpenAI(api_key=config.OPENAI)
linear = Linear(api_key=config.LINEAR)

class PlannedProject(BaseModel):
    plan: Plan
    project: LinearProject
    milestones: list[LinearMilestone]
    labels: list[LinearLabel]
    issues: list[dict]

def generate_plan(report: str) -> PlannedProject:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful planner that generates a plan for a project based on a report."},
            {"role": "user", "content": report},
        ],
        response_format=Plan,
    )
    plan = completion.choices[0].message.parsed
    project = linear.create_project(plan.project.name, plan.project.description)
    linear_milestones: dict[str, LinearMilestone] = {}
    linear_labels: dict[str, LinearLabel] = {}
    issues: list[dict] = []
    for milestone in plan.milestones:
        linear_milestone = linear.create_project_milestone(project.id, milestone.name, milestone.description)
        linear_milestones[milestone.name] = linear_milestone
    for label in plan.labels:
        linear_label = linear.create_project_label(label.name)
        linear_labels[label.name] = linear_label
    for issue in plan.issues:
        issue_label_ids = [linear_labels[label].id for label in issue.labels if label in linear_labels]
        issue_milestone_id = linear_milestones[issue.milestone].id if issue.milestone in linear_milestones else None
        issues.append(linear.create_issue(issue.title, issue.description, project.id, issue_label_ids, issue_milestone_id))
    return PlannedProject(plan=plan, project=project, milestones=list(linear_milestones.values()), labels=list(linear_labels.values()), issues=issues)
