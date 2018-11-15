import os
import subprocess
from shutil import copyfile
from os import path

# pip install PyGithub. Lib operates on remote github to get issues
import math
from time import sleep

from github import Github
import re
import github.Issue

import argparse

# pip install GitPython. Lib operates on local repo to get commits
import git as local_git

from common import translate_long_sentence, translate_tokens, sentence_contains_chinese, translate_intermingual_sentence


class MyIssue:
    def __init__(self, issue_id, content, create_time, close_time):
        self.issue_id = issue_id
        self.content = content
        self.create_time = create_time
        self.close_time = close_time

    def __str__(self):
        content_str = "\n".join(self.content)
        content_str = re.sub("[,\r\n]+", " ", content_str)
        return "{},{},{}\n".format(self.issue_id, content_str, self.close_time)


class MyCommit:
    def __init__(self, commit_id, summary, diffs, commit_time):
        self.commit_id = commit_id
        self.summary = summary
        self.diffs = diffs
        self.commit_time = commit_time

    def __str__(self):
        summary = re.sub("[,\r\n]+", " ", self.summary)
        diffs = " ".join(self.diffs)
        diffs = re.sub("[,\r\n]+", " ", diffs)
        return "{},{},{},{}\n".format(self.commit_id, summary, diffs, self.commit_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Github script")
    parser.add_argument("-u", help="user name")
    parser.add_argument("-p", help="password")
    parser.add_argument("-d", help="download path")
    parser.add_argument("-r", help="repo path in github")
    parser.add_argument("-t", action="store_true", help="boolean value determine whether do translation")
    args = parser.parse_args()
    git = Github(args.u, args.p)
    git.get_user()

    translate_project_flag = args.t
    EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

    output_dir = os.path.join("git_projects", args.r)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    issue_dict = dict()
    repo = git.get_repo(args.r)
    issues = repo.get_issues(state="all")

    issue_file_path = os.path.join(output_dir, "issue.csv")
    if not os.path.isfile(issue_file_path):
        print("creating issue.csv")
        with open(issue_file_path, "w", encoding='utf8') as fout:
            fout.write("issue_id,issue_content,closed_at\n")
            for issue in issues:
                issue_number = issue.number
                print(issue_number)
                content = []
                content.append(issue.title)
                content.append(issue.body)
                issue_close_time = issue.closed_at
                issue_create_time = issue.created_at
                for comment in issue.get_comments():
                    content.append(comment.body)
                myissue = MyIssue(issue_number, content, issue_create_time, issue_close_time)
                fout.write(str(myissue))

    repo_url = "git@github.com:{}.git".format(args.r)
    repo_name = repo_url.split("/")[1]
    clone_path = os.path.join(args.d, repo_name)
    if not os.path.exists(clone_path):
        local_git.Repo.clone_from(repo_url, clone_path, branch='master')
    local_repo = local_git.Repo(clone_path)

    commit_file_path = os.path.join(output_dir, "commit.csv")
    if not os.path.isfile(commit_file_path):
        print("creating commit.csv...")
        with open(commit_file_path, 'w', encoding="utf8") as fout:
            fout.write("commit_id,commit_summary, commit_diff,commit_time\n")
            for i, commit in enumerate(local_repo.iter_commits()):
                print("commit #{}".format(i))
                id = commit.hexsha
                summary = commit.summary
                create_time = commit.committed_datetime
                parent = commit.parents[0] if commit.parents else EMPTY_TREE_SHA
                differs = set()
                for diff in commit.diff(parent, create_patch=True):
                    diff_lines = str(diff).split("\n")
                    for diff_line in diff_lines:
                        if diff_line.startswith("+") or diff_line.startswith("-") and '@' not in diff_line:
                            differs.add(diff_line)
                commit = MyCommit(id, summary, differs, create_time)
                fout.write(str(commit))

    # Translate the commit and issue
    trans_out_dir = os.path.join(output_dir, "translated_data")
    if not os.path.isdir(trans_out_dir):
        os.mkdir(trans_out_dir)
    trans_issue_file_path = os.path.join(trans_out_dir, "issue.csv")
    trans_commit_file_path = os.path.join(trans_out_dir, "commit.csv")
    # issue_token_file_path = os.path.join(output_dir, "clean_token_data", "issue.csv")
    # commit_token_file_path = os.path.join(output_dir, "clean_token_data", "commit.csv")

    if translate_project_flag is True:
        print("Translating issue...")
        partition_size = 14000
        with open(trans_issue_file_path, 'w', encoding='utf8') as fout, open(issue_file_path, encoding='utf8') as fin:
            for i, line in enumerate(fin):
                if i == 0:
                    fout.write(line)
                    continue
                print(i)
                issue_id, issue_content = line.strip("\n\t\r").split(",")
                translated_issue_content = translate_intermingual_sentence(issue_content)
                fout.write("{},{}\n".format(issue_id, translated_issue_content))

        print("Translate commit...")
        with open(trans_commit_file_path, 'w', encoding='utf8') as fout, open(commit_file_path,
                                                                              encoding='utf8') as fin:
            for i, line in enumerate(fin):
                if i == 0:
                    fout.write(line)
                    continue
                print(i)
                commit_id, commit_summary, commit_content = line.strip("\n\t\r").split(",")
                translated_commit_summary = translate_intermingual_sentence(commit_summary)
                translated_commit_content = translate_intermingual_sentence(commit_content)
                fout.write("{},{},{}\n".format(commit_id, translated_commit_summary, translated_commit_content))

    # Extract links from the commits
    with open(os.path.join(output_dir, "links.csv"), 'w', encoding='utf8') as fout, \
            open(issue_file_path, encoding='utf8') as issue_in, \
            open(commit_file_path, encoding='utf8') as commit_in:
        issue_ids = set()
        fout.write("issue_id,commit_id\n")
        for line in issue_in:
            issue_ids.add(line.split(',')[0])
        for line in commit_in:
            summary = line.split(',')[1]
            commit_id = line.split(",")[0]
            res = re.search('#\d+', summary)
            if res is not None:
                linked_issue_id = res.group(0)
                issue_id = linked_issue_id.strip("#")
                if issue_id not in issue_ids:
                    print("{} is not in the issue file".format(issue_id))
                fout.write("{},{}\n".format(issue_id, commit_id))
