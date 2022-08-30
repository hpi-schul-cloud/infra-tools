# workflow-actions-extractor

This python scricpt searches all repositories of an organization for actions used inside workflows and extracts them into an CSV-file. It contains the names of the repository, workflow and action.

The script requires a GitHub Personal Access Token and the library PyGitHub.

For usage see `python3 workflow-actions-extractor.py --help`