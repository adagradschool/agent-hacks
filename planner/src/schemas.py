from pydantic import BaseModel, Field

class LabelCreate(BaseModel):
    name: str = Field(..., description="A semantic label for the issue. Example: 'Nutrition', 'Excercise', 'Lifestyle' for a fitness app.")

class MilestoneCreate(BaseModel):
    name: str = Field(..., description="Denotes a phase of the project. Example: 'Planning', 'Execution', 'Review'")
    description: str = Field(..., description="A brief description of the milestone. This is useful in tracking the progress of the project.")

class ProjectCreate(BaseModel):
    name: str = Field(..., description="The name of the project.")
    description: str = Field(..., description="A brief description of the project.")

class IssueCreate(BaseModel):
    title: str = Field(..., description="The title of the issue. It should be actionable and concise.")
    description: str = Field(..., description="A detailed description of the issue. It should have a clear objective and a clear success criteria.")
    labels: list[str] = Field(..., description="A list of labels associated with the issue. This is useful in categorizing issues.")
    milestone: str = Field(..., description="The name of the milestone this issue belongs to. This is useful in tracking the progress of the project.")

class Plan(BaseModel):
    project: ProjectCreate = Field(..., description="Details about the project.")
    milestones: list[MilestoneCreate] = Field(..., description="A list of milestones for the project.")
    labels: list[LabelCreate] = Field(..., description="A list of labels to be used in the project.")
    issues: list[IssueCreate] = Field(..., description="A list of issues for the project.")
    