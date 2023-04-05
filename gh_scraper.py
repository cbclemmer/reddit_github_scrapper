import os
import sys
import re
import json
from urllib.parse import urlparse
from util import open_file, is_github_link, cleanup_link, is_repo_starred, get_repo_url

import praw
import requests
from github import Github

reddit_client_id = open_file('keys/reddit_id.txt')
reddit_client_secret = open_file('keys/reddit_secret.txt')
github_access_token = open_file('keys/github.txt')
reddit_user_agent = 'github_scraper'

print('Reddit ID: ' + reddit_client_id)
print('Reddit Secret: ' + reddit_client_secret)
print('Github Token: ' + github_access_token)

reddit = praw.Reddit(
    client_id=reddit_client_id,
    client_secret=reddit_client_secret,
    user_agent=reddit_user_agent
)

# Set up PyGithub
github = Github(github_access_token)

# Define the subreddit and how many posts to scrape
subreddit_name = 'all'
if len(sys.argv) > 1:
    subreddit_name = sys.argv[1]
num_posts = 100

# Define a regex pattern for GitHub links
github_pattern = re.compile(r'(https?:\/\/github\.com\/[^\s\)\]]+)')

# Scrape the subreddit
subreddit = reddit.subreddit(subreddit_name)
print('Fetching reddit posts for r/' + subreddit_name)
posts = subreddit.new(limit=num_posts)

# Collect GitHub links
github_links = set()
for post in posts:
    # print(post.keys())
    # If the post is a crosspost, get the original post
    url = ''
    body = ''
    if hasattr(post, 'crosspost_parent_list'):
        original_post = json.loads(json.dumps(post.crosspost_parent_list[0]))
        url = original_post['url']
        body = original_post['selftext']
    else:
        original_post = post
        url = post.url
        body = post.selftext

    print('\tPost: ' + post.title)
    # Check if the post URL is a GitHub link
    if is_github_link(url):
        gh_url = cleanup_link(url)
        print('\t\tFound github link in url: ' + gh_url)
        github_links.add(gh_url)

    # Check the post body for GitHub links
    for match in github_pattern.finditer(body):
        gh_url = cleanup_link(match.group(1))
        print('\t\tFound github link in body: ' + gh_url)
        github_links.add(gh_url)

print('\n\nGetting current github stars')
github_user = github.get_user()
starred_repos = github_user.get_starred()

print('\n\nStarring new repos')
# Star the repositories on GitHub
new_stars = 0
for link in github_links:
    repo_url = get_repo_url(link)
    if repo_url:
        try:
            repo_path = urlparse(repo_url).path.strip('/')
            repo = github.get_repo(repo_path)
            if not is_repo_starred(repo, starred_repos):
                github_user.add_to_starred(repo)
                print(f'\tStarred repository: {repo_path}')
                new_stars += 1
        except Exception as e:
            print(f'\tError starring repository {repo_url}: {e}')
    else:
        print(f'Invalid repository URL: {link}')

print(f'Starred {new_stars} new GitHub repositories')
