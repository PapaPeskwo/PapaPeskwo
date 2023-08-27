import re
import requests
import sys

# Get the token from command line arguments
token = sys.argv[1]

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

# Regex to match the lines in the README table
regex = r"\|\s*\[([^\]]+)\]\(https://github.com/([^\)]+)\)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"

with open("README.md", "r") as file:
    content = file.read()

# Extract the projects section from the README
matches = list(re.finditer(regex, content))

if not matches:
    print("No project entries found.")
    projects_end = content.index("## Certificates")  # or wherever your projects section typically ends
else:
    projects_end = max([m.end() for m in matches])


projects_section = content[projects_start:projects_end]

# Collect all repository details in a list
repos = []

for match in re.finditer(regex, projects_section):
    repo_url, repo_fullname, description, _ = match.groups()
    repo_api_url = f"https://api.github.com/repos/{repo_fullname}/commits/master"
    response = requests.get(repo_api_url, headers=headers)
    response.raise_for_status()
    last_updated = response.json()["commit"]["committer"]["date"]
    formatted_date = "/".join(reversed(last_updated.split("T")[0].split("-")))

    repos.append({
        "repo_url": repo_url,
        "repo_fullname": repo_fullname,
        "description": description,
        "formatted_date": formatted_date,
        "last_updated": last_updated
    })

# Sort the repositories based on the last_updated time
sorted_repos = sorted(repos, key=lambda x: x["last_updated"], reverse=True)

# Construct the new projects section
new_projects = "## Projects\n| Project Name | Project Description | Last Updated: |\n| --- | --- | --- |\n"
for repo in sorted_repos:
    new_line = f"| [{repo['repo_url']}](https://github.com/{repo['repo_fullname']}) | {repo['description']} | {repo['formatted_date']} |\n"
    new_projects += new_line

# Replace the old projects section with the new one
new_content = content.replace(projects_section, new_projects)

# Overwrite README if there are changes
if new_content != content:
    with open("README.md", "w") as file:
        file.write(new_content)
