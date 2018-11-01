import os
import subprocess
from shutil import copyfile
from os import path

# pip install PyGithub. Lib operates on remote github to get issues
from github import Github
import re
import github.Issue

import argparse

# pip install GitPython. Lib operates on local repo to get commits
import git as local_git


class MyIssue:
    def __init__(self, issue_id, content):
        self.issue_id = issue_id
        self.content = content

    def __str__(self):
        content_str = "\n".join(self.content)
        content_str = re.sub("[,\r\n]+", " ", content_str)
        return "{},{}\n".format(self.issue_id, content_str)


class MyCommit:
    def __init__(self, commit_id, summary, diffs):
        self.commit_id = commit_id
        self.summary = summary
        self.diffs = diffs

    def __str__(self):
        summary = re.sub("[,\r\n]+", " ", self.summary)
        diffs = " ".join(self.diffs)
        diffs = re.sub("[,\r\n]+", " ", diffs)
        return "{},{},{}\n".format(self.commit_id, summary, diffs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Github script")
    parser.add_argument("-u", help="user name")
    parser.add_argument("-p", help="password")
    parser.add_argument("-d", help="download path")
    parser.add_argument("-r", help="repo path in github")
    args = parser.parse_args()
    git = Github(args.u, args.p)
    git.get_user()

    EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

    output_dir = os.path.join("git_projects", args.r)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    issue_dict = dict()
    repo = git.get_repo(args.r)
    issues = repo.get_issues(state="closed")
    with open(os.path.join(output_dir, "issue.csv"), "w", encoding='utf8') as fout:
        fout.write("issue_id,issue_content\n")
        for issue in issues:
            issue_number = issue.number
            print(issue_number)
            content = []
            content.append(issue.title)
            content.append(issue.body)
            for comment in issue.get_comments():
                content.append(comment.body)
            fout.write(str(MyIssue(issue_number, content)))

    repo_url = "git@github.com:{}.git".format(args.r)
    repo_name = repo_url.split("/")[1]
    clone_path = os.path.join(args.d, repo_name)
    if not os.path.exists(clone_path):
        local_git.Repo.clone_from(repo_url, clone_path, branch='master')
    local_repo = local_git.Repo(clone_path)

    with open(os.path.join(output_dir, "commit.csv"), 'w', encoding="utf8") as fout:
        fout.write("commit_id,commit_summary, commit_diff")
        for commit in local_repo.iter_commits():
            id = commit.hexsha
            summary = commit.summary
            parent = commit.parents[0] if commit.parents else EMPTY_TREE_SHA
            differs = set()
            for diff in commit.diff(parent, create_patch=True):
                diff_lines = str(diff).split("\n")
                for diff_line in diff_lines:
                    if diff_line.startswith("+") or diff_line.startswith("-") and '@' not in diff_line:
                        differs.add(diff_line)
            fout.write(str(MyCommit(id, summary, differs)))
