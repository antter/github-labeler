import pandas as pd
import numpy as np
from tqdm import tqdm
import collections
import datetime
import time
from github import Github
import os
import itertools
import argparse

# command line functionality
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--user', default = '', help = 'username of user/organization')
group.add_argument('--repo', default = '', help = 'name of repo in format user/repo-name')
args = parser.parse_args()

g = Github(os.getenv('GITHUB_ACCESS_TOKEN'))

# username of person or organization
USER = args.user
# OR  name of repo org/repo-name
REPO = args.repo

# add all repos to list, or create list of one
repos_ = []

if USER:
    org = g.get_user(USER)
    repos = org.get_repos()
    for repo in repos:
        repos_.append(repo)
else:
    to_add = g.get_repo(REPO)
    repos_.append(to_add)

def get_issues_for_repo(repo):
    """
    takes in a pygithub repo object and returns the list of pygithub issue objects
    """
    issues = []
    issues_left = True
    MAX = datetime.datetime.min
    exceptions = 0
    while issues_left:
        issues_left = False
        try:
            for issue in repo.get_issues(state = 'all', direction = 'asc', since = MAX):        
                MAX = issue.created_at
                try:
                    if issue.pull_request is None:
                        issues.append(issue)
                except:
                    exceptions += 1
                    continue
        except Exception as e:
            print(len(issues), 'issues added for', {repo.full_name})
            print('SLEEPING NOW')
            time.sleep(60*61)
            issues_left = True
    return issues

# add in all issues
all_issues = {}

if USER:
    print('getting issues for repos')
    for repo in tqdm(repos_):
        all_issues[repo.full_name] = get_issues_for_repo(repo)
else:
    repo = repos_[0]
    all_issues[repo.full_name] = get_issues_for_repo(repo)
    
total_issues = sum([len(b) for a,b in all_issues.items()])
print(total_issues, 'total issues')

# create dataframe for issues
data = []

for repo, issues in all_issues.items():
    for issue in issues:
        data.append([repo, issue.title, issue.body, issue.labels, issue.created_at])
    
df = pd.DataFrame(data, columns = ['repo', 'title', 'body', 'labels', 'created_at'])
df = df.loc[df.drop(['labels'] ,axis = 1).drop_duplicates().index]

# process labels (tab-separated names)
list_issues = lambda x: '\t'.join([issue.name for issue in x])
df['labels'] = df['labels'].apply(lambda x: np.nan if not x else list_issues(x))

# give short report 
labels_lists = [labels.split('\t') for labels in df['labels'].dropna()]
all_items = list(itertools.chain.from_iterable(labels_lists))
counter = collections.Counter(all_items)
print()
print('Most common issues:')
for label, N in counter.most_common(10):
    print(f'{label}: {N}')
    
# save dataframe
SAVENAME = USER if USER else REPO.replace('/', '-')
SAVENAME += '.csv'
df.to_csv(os.path.join('../data',SAVENAME), index = None)
