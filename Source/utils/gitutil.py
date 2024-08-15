import requests


class GitHubWorkflowDispatcher:
    def __init__(self, token, owner, repo):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def dispatch_workflow(self, workflow_id, branch="master", inputs=None):
        if inputs is None:
            inputs = {}

        response = requests.post(
            f"https://adc.github.trendmicro.com/api/v3/repos/{self.owner}/{self.repo}/actions/workflows/{workflow_id}/dispatches",
            headers=self.headers,
            json={
                "ref": branch,
                "inputs": inputs
            },
        )

        response.raise_for_status()
