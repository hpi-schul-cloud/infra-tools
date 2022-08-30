import github
import base64
import sys
import csv
import yaml
import argparse

# Returns a nested dictionary (Name of Repository -> Workflow file -> Set of action strings)
def get_organization_actions(organization: github.Organization.Organization):
    actions = {}
    repos = organization.get_repos()
    print(repos.totalCount, "repositories found")
    for repo in repos:
        actions[repo.name] = get_repo_actions(repo)
    return actions

# Returns a dictionary (Workflow file -> Set of action strings)
def get_repo_actions(repo: github.Repository.Repository):
    actions = {}
    try:
        workflow_files = repo.get_contents(".github/workflows")
    except github.UnknownObjectException as e:
        # No workflow files in the repository
        workflow_files = []
    print("Repository", repo.name, "has", len(workflow_files), "workflow files")
    for file in workflow_files:
        try:
            if file.encoding != "base64":
                raise ValueError("Unexpected content encoding: " + file.encoding)
            content = base64.b64decode(file.content).decode("UTF-8")
            workflow_actions = get_actions_from_workflow(content)
            actions[file.name] = set(workflow_actions) # Use set to eliminate duplicates
        except Exception as e:
            print("Couldn't parse workflow", file.name, "in", repo.name, "Exception:", e, file = sys.stderr)
    return actions

# Parses a YAML-String and extracts the used actions as list
def get_actions_from_workflow(workflow_content: str):
    # PyYAML has a problem with parsing a tab even in places where it is allowed
    # https://github.com/yaml/pyyaml/issues/306
    # -> Replace all tabs with spaces
    untabbed_content = workflow_content.replace("\t","    ")
    dict = yaml.safe_load(untabbed_content)
    if "jobs" in dict:
        return get_actions_from_jobs(dict["jobs"])
    else:
        return []

def get_actions_from_jobs(jobs: dict) -> list:
    actions = []
    for name, details in jobs.items():
        if "uses" in details:
            actions.append(details["uses"])
        if "steps" in details and isinstance(details["steps"], list):
            actions.extend(get_actions_from_steps(details["steps"]))
    return actions

def get_actions_from_steps(steps: list):
    actions = []
    for step in steps:
        if "uses" in step:
            actions.append(step["uses"])
    return actions


parser = argparse.ArgumentParser("Searches all repositories of an organization for actions used in jobs inside workflows and extracts them into an CSV file")
parser.add_argument("github_token", help = "Personal access token generated on GitHub, no special scopes/permissions required")
parser.add_argument("organization", help = "Name of the organization (from the URL) whose repositories should be analyzed")
parser.add_argument("-o", "--output_file", default = "actions.csv")
args = parser.parse_args()

g = github.Github(args.github_token)
organization = g.get_organization(args.organization)
actionsdict = get_organization_actions(organization)

#Export to csv file
with open(args.output_file,"w") as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(["repository","workflow","action"])
    for repo, value in actionsdict.items():
        for workflow, actions in value.items():
            for action in actions:
                csvwriter.writerow([repo, workflow, action])