import re
from urllib.parse import urlparse

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# Function to check if a URL is a GitHub link
def is_github_link(url):
    domain = urlparse(url).netloc
    return domain == 'github.com' or domain == 'www.github.com'

# Function to clean up the extracted GitHub links
def cleanup_link(link):
    # Remove trailing characters like parentheses, brackets, and periods
    link = re.sub(r'[\)\]\.]+$', '', link)
    return link

def is_repo_starred(repo, starred_repos):
    for starred_repo in starred_repos:
        if repo.id == starred_repo.id:
            return True
    return False

# Function to extract the main repository URL from any GitHub URL
def get_repo_url(url):
    path_parts = urlparse(url).path.strip('/').split('/')
    if len(path_parts) >= 2:
        return f'https://github.com/{path_parts[0]}/{path_parts[1]}'
    return None