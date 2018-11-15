# A script add time to clean_token_data
import argparse
import os
from common import GIT_PROJECTS


def read_time(path) -> dict:
    time_dict = dict()
    with open(path, encoding='utf8') as fin:
        for i, line in enumerate(fin):
            line = line.strip("\n\t\r")
            if i == 0:
                continue
            parts = line.split(",")
            id = parts[0]
            time = parts[-1]
            time_dict[id] = time
    return time_dict


def append_time(file_path, time_dict):
    tmp = []
    with open(file_path, 'r', encoding='utf8') as fin:
        for line in fin:
            tmp.append(line)

    with open(file_path, 'w', encoding='utf8') as fout:
        for i, line in enumerate(tmp):
            line = line.strip("\n\r\t,")
            if i == 0:
                fout.write("{},{}\n".format(line, "time"))
                continue
            id = line.split(",")[0]
            time = time_dict[id]
            fout.write("{},{}\n".format(line, time))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Experiment 2")
    parser.add_argument("--git_repo_path", help="the repo path of the dataset e.g alibaba/canal")
    args = parser.parse_args()
    data_dir = os.path.join(GIT_PROJECTS, args.git_repo_path)

    raw_commit_path = os.path.join(data_dir, "commit.csv")
    raw_issue_path = os.path.join(data_dir, "issue.csv")
    commit_time_dict = read_time(raw_commit_path)
    issue_time_dict = read_time(raw_issue_path)

    clean_token_data_dir = os.path.join(data_dir, "clean_token_data")
    commit_path = os.path.join(clean_token_data_dir, "commit.csv")
    issue_path = os.path.join(clean_token_data_dir, "issue.csv")
    # append_time(commit_path, commit_time_dict)
    # append_time(issue_path, issue_time_dict)

    translated_clean_token_data_dir = os.path.join(data_dir, "translated_data", "clean_translated_tokens")
    translated_commit_path = os.path.join(translated_clean_token_data_dir, "commit.csv")
    translated_issue_path = os.path.join(translated_clean_token_data_dir, "issue.csv")
    append_time(translated_commit_path, commit_time_dict)
    append_time(translated_issue_path, issue_time_dict)
