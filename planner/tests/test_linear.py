from src.linear import Linear
from src.config import config
import random
import string
import pytest
linear = Linear(config.LINEAR)

def _random_string(length: int = 10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def test_linear_teams():
    teams = linear.teams()
    assert teams is not None
    assert len(teams) > 0
    assert teams[0]['id'] is not None
    assert teams[0]['name'] is not None
    assert teams[0]['id'] == linear.team_id

@pytest.mark.skip(reason="Test calls actual API")
def test_linear_create_project():
    project = linear.create_project("Test Project", linear.team_id)
    assert project is not None
    assert project['name'] == "Test Project"
    assert project['id'] is not None

@pytest.mark.skip(reason="Test calls actual API")
def test_linear_create_project_milestone():
    project = linear.create_project("Test Project", linear.team_id)
    milestone = linear.create_project_milestone(project['id'], "Test Milestone")
    assert milestone is not None
    assert milestone['name'] == "Test Milestone"
    assert milestone['id'] is not None

@pytest.mark.skip(reason="Test calls actual API")
def test_linear_create_project_label():
    label = linear.create_project_label("Test Label 2")
    assert label is not None
    assert label['name'] == "Test Label 2"
    assert label['id'] is not None
    
@pytest.mark.skip(reason="Test calls actual API")
def test_linear_create_issue():
    project = linear.create_project(_random_string(), linear.team_id)
    milestone = linear.create_project_milestone(project['id'], _random_string())
    label = linear.create_project_label(_random_string())
    title = _random_string()
    description = _random_string()
    issue = linear.create_issue(title = title, description=description, project_id=project['id'], milestone_id=milestone['id'], label_ids=[label['id']])
    assert issue is not None
    assert issue['issue']['title'] == title
    assert issue['issue']['id'] is not None
    assert issue['issue']['labels']['nodes'][0]['name'] == label['name']
    assert issue['issue']['projectMilestone']['name'] == milestone['name']