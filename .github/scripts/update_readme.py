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

new_content = content
for match in re.finditer(regex, content):
    repo_label, repo_fullname, description, date = match.groups()
    
    # Extracting repository name from repo_fullname
    repo_name = repo_fullname.split("/")[-1]
    
    repo_api_url = f"https://api.github.com/repos/{repo_fullname}/commits/master"
    response = requests.get(repo_api_url, headers=headers)
    response.raise_for_status()
    last_updated = response.json()["commit"]["committer"]["date"]
    last_updated_date = last_updated.split("T")[0]
    formatted_date = "/".join(reversed(last_updated_date.split("-")))

    new_line = f"| [{repo_name}](https://github.com/{repo_fullname}) | {description} | {formatted_date} |"
    new_content = new_content.replace(match.group(0), new_line)

# Overwrite README if there are changes
if new_content != content:
    with open("README.md", "w") as file:
        file.write(new_content)
