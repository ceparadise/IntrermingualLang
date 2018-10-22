import os
import subprocess
from shutil import copyfile
from os import path

from github import Github
import re
import github.Issue

import argparse
import git as local_git


class MyIssue:
    def __init__(self, issue_id, content):
        self.issue_id = issue_id
        self.content = content

    def __str__(self):
        content_str = "\n".join(self.content)
        content_str = re.sub("[,\r\n]+", " ", content_str)
        return "{},{}\n".format(self.issue_id, content_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Github script")
    parser.add_argument("-u", help="user name")
    parser.add_argument("-p", help="password")
    parser.add_argument("-d", help="download path")
    parser.add_argument("-r", help="repo path in github")
    args = parser.parse_args()
    git = Github(args.u, args.p)
    git.get_user()

    output_dir = os.path.join("git_projects", args.r)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    issue_dict = dict()
    repo = git.get_repo(args.r)
    # issues = repo.get_issues()
    # with open(os.path.join(output_dir, "issue.csv"), "w", encoding='utf8') as fout:
    #     fout.write("issue_id,issue_content\n")
    #     for issue in issues:
    #         issue_number = issue.number
    #         print(issue_number)
    #         content = []
    #         content.append(issue.title)
    #         content.append(issue.body)
    #         for comment in issue.get_comments():
    #             content.append(comment.body)
    #         fout.write(str(MyIssue(issue_number, content)))

    repo_url = "git@github.com:alibaba/canal.git"
    local_git.refresh("/g/Tool/Git/bin")
    local_git.Repo.clone_from(repo_url, os.path.join(args.d, 'repo'), branch='master')
