import json
import requests
from pydantic import BaseModel

class LinearTeam(BaseModel):
    id: str
    name: str

class LinearProject(BaseModel):
    id: str
    name: str

class LinearMilestone(BaseModel):
    id: str
    name: str

class LinearLabel(BaseModel):
    id: str
    name: str

class LinearQueryException(Exception):
    def __init__(self, errors: list[dict]):
        self.errors = errors
        super().__init__(f"Linear Query Exception: {errors}")
        self.errors = errors

    def __str__(self):
        return f"LinearQueryException: {self.errors}"
    def __repr__(self):
        return f"LinearQueryException: {self.errors}"

class Linear:
    def __init__(self, api_key: str):
        self.set_url('https://api.linear.app/graphql')
        self.set_api_key(api_key)
        self.headers = {
            "Authorization" : self.LINEAR_API_KEY
        }
        self.team_id = "a53d1e00-ef0b-40e1-8afb-62c97a404556"
        
        
    def set_url(self, url):
        self.graphql_url = url
    def set_api_key(self, LINEAR_API_KEY):
        self.LINEAR_API_KEY = LINEAR_API_KEY
    def query_grapql(self, query):
        r = requests.post(self.graphql_url, json={
            "query": query
        }, headers=self.headers)
        response = json.loads(r.content)
        if 'errors' in response:
            raise LinearQueryException(response["errors"])
        return response
    def query_basic_resource(self, resource=''):
        resource_response = self.query_grapql(
            """
                query Resource {"""+resource+"""{nodes{id,name}}}
            """
        )
        return resource_response["data"][resource]["nodes"]
    
    def create_issue(self, title, description='', project_id='', label_ids: list = None, milestone_id=''):
        label_ids_str = json.dumps(label_ids) if label_ids else "[]"

        create_response = self.query_grapql(
            """
            mutation IssueCreate {{
              issueCreate(
                input: {{
                    title: "{title}"
                    description: "{description}"
                    projectId: "{project_id}"
                    teamId: "{team_id}"
                    labelIds: {label_ids_str}
                    projectMilestoneId: "{milestone_id}"
                }}
              ) {{
                success
                issue {{
                  id
                  title
                  labels {{
                    nodes {{
                      id
                      name
                    }}
                  }}
                  projectMilestone {{
                      id
                      name
                  }}
                }}
              }}
            }}
            """.format(title=title, description=description, project_id=project_id, team_id=self.team_id, label_ids_str=label_ids_str, milestone_id=milestone_id)
        )
        return create_response['data']['issueCreate']['issue']
    
    def create_project(self, name: str, description: str = '') -> LinearProject:
        create_response = self.query_grapql(
            """
            mutation ProjectCreate {{
              projectCreate(
                input: {{
                  name: "{name}"
                  description: "{description}"
                  teamIds: ["{team_id}"]
                }}
              ) {{
                success
                project {{
                  id
                  name
                }}
              }}
            }}
            """.format(name=name, description=description, team_id=self.team_id)
        )
        return LinearProject(**create_response['data']['projectCreate']['project'])

    def create_project_milestone(self, project_id: str, name: str, description: str = ''):
        create_response = self.query_grapql(
            """
            mutation ProjectMilestoneCreate {{
              projectMilestoneCreate(
                input: {{
                  name: "{name}"
                  description: "{description}"
                  projectId: "{project_id}"
                }}
              ) {{
                success
                projectMilestone {{
                  id
                  name
                }}
              }}
            }}
            """.format(name=name, description=description, project_id=project_id)
        )
        return LinearMilestone(**create_response['data']['projectMilestoneCreate']['projectMilestone'])

    def create_project_label(self, name: str):
        try:
          create_response = self.query_grapql(
              """
              mutation LabelCreate {{
                issueLabelCreate(
                  input: {{
                    name: "{name}"
                    teamId: "{team_id}" 
                  }}
                ) {{
                  success
                  issueLabel {{
                    id
                    name
                  }}
                }}
              }}
              """.format(name=name, team_id=self.team_id)
          )
        except Exception as e:
            # Handle the case where the label already exists
            labels = self.query_basic_resource('issueLabels')
            for label in labels:
                if label['name'] == name:
                    return LinearLabel(**label)
            raise Exception(f"Label {name} not found")
        return LinearLabel(**create_response['data']['issueLabelCreate']['issueLabel'])

    def teams(self):
        return self.query_basic_resource('teams')
    def states(self):
        return self.query_basic_resource('workflowStates')
    def projects(self):
        return self.query_basic_resource('projects')