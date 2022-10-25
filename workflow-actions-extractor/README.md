# workflow-actions-extractor

This python scricpt searches all repositories of an organization for actions used inside workflows and extracts them into an CSV-file. It contains the names of the repository, workflow and action.

The script requires a GitHub Personal Access Token (scope "repo" is necessary for private repositories) and the libraries PyGitHub and PyYAML.
You can install them with `pip install -r requirements.txt`.

For usage see `python3 workflow-actions-extractor.py --help`
