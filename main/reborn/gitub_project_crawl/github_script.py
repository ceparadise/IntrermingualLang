from github import Github
import github.Issue

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Github script")
    parser.add_argument("-u", help="user name")
    parser.add_argument("-p", help="password")
    args = parser.parse_args()
    git = Github(args.u, args.p)
    git.get_user()

    org = git.get_organization('alibaba')
    repo = org.get_repo('canal')
    issues = repo.get_issues()
    for issue in issues:
        print("============")
        issueNumber = issue.number
        print(issue.title)

        print(issue.body)
        for comment in issue.get_comments():
            print(comment.body)
        print("--------------")



