import math
import os

# pip install PyGithub. Lib operates on remote github to get issues

from github import Github
import re

import argparse

# pip install GitPython. Lib operates on local repo to get commits
import git as local_git
from google.cloud import translate

CHINESE_CHAR_PATTERN = re.compile("[\u4e00-\u9fff]+")
KOREAN_CHAR_PATTERN = re.compile("[\u3131-\ucb4c]+")
JAPANESS_CHAR_PATTERN = re.compile("[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]+")
EURPO_CHAR_PATTERN = re.compile("[\u00c0-\u017e]+")
LANG_PATTERN = [CHINESE_CHAR_PATTERN, KOREAN_CHAR_PATTERN, JAPANESS_CHAR_PATTERN]

translator = translate.Client()


def sentence_contains_chinese(sentence: str) -> bool:
    return CHINESE_CHAR_PATTERN.search(sentence) is not None


def sentence_contains_foreign_lang(sentence: str) -> bool:
    flag = False
    for pattern in LANG_PATTERN:
        if pattern.search(sentence) is not None:
            flag = True
    return flag


def translate_long_sentence(sentence, partition_size=14000):
    """
    Translate a long sentence into English.
    :param sentence:
    :param partition_size:
    :return:
    """
    trans_content = []
    for par in range(math.ceil(len(sentence) / partition_size)):
        part = sentence[par * partition_size: (par + 1) * partition_size]
        try:
            trans_part = translator.translate(part)["translatedText"]
        except Exception as e:
            print("Exception when translating sentence {}, exception is {}".format(part, e))
            trans_part = part
        trans_content.append(trans_part)
    return " ".join(trans_content)


def translate_intermingual_sentence(sentence: str) -> str:
    """
    Find out the Chinese sentences in a long string, translate those parts and return a pure english version sentence
    of the input
    :param sentence:
    :return:
    """
    sentence_segments_by_space = sentence.split()
    translated_sentence = []
    for sentence_segment in sentence_segments_by_space:
        if sentence_contains_foreign_lang(sentence_segment):
            sentence_segment = re.sub("[^\w]+", " ", sentence_segment)
            trans_segment = translate_long_sentence(sentence_segment)
        else:
            trans_segment = sentence_segment
        translated_sentence.append(trans_segment)
    return " ".join(translated_sentence)


class MyIssue:
    def __init__(self, issue_id, content, create_time, close_time):
        self.issue_id = issue_id
        self.content = content
        self.create_time = create_time
        self.close_time = close_time

    def __str__(self):
        self.content = [x for x in self.content if x is not None]
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


class RepoCollector:
    def __init__(self, user_name, passwd, download_path, repo_path, do_translation):
        self.user_name = user_name
        self.passwd = passwd
        self.download_path = download_path
        self.repo_path = repo_path
        self.do_translate = do_translation

    def run(self):
        git = Github(self.user_name, self.passwd)
        git.get_user()

        translate_project_flag = self.do_translate
        EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

        output_dir = os.path.join("git_projects", self.repo_path)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        issue_dict = dict()
        repo = git.get_repo(self.repo_path)
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

        repo_url = "git@github.com:{}.git".format(self.repo_path)
        repo_name = repo_url.split("/")[1]
        clone_path = os.path.join(self.download_path, repo_name)
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

            if os.path.isfile(trans_issue_file_path):
                with open(trans_issue_file_path, 'r', encoding='utf8') as fin:
                    translatedLines = fin.readlines()
            else:
                translatedLines = []

            with open(trans_issue_file_path, 'w', encoding='utf8') as fout, open(issue_file_path,
                                                                                 encoding='utf8') as fin:
                for i, line in enumerate(fin):
                    if i == 0:
                        fout.write(line)
                        continue
                    print(i)
                    if i < len(translatedLines):
                        trans_line = translatedLines[i].strip("\n\t\r")
                        fout.write(trans_line + "\n")
                    else:
                        issue_id, issue_content, issue_close_time = line.strip("\n\t\r").split(",")
                        translated_issue_content = translate_intermingual_sentence(issue_content)
                        fout.write("{},{},{}\n".format(issue_id, translated_issue_content, issue_close_time))

            print("Translate commit...")

            if os.path.isfile(trans_commit_file_path):
                with open(trans_commit_file_path, 'r', encoding='utf8') as fin:
                    translatedLines = fin.readlines()
            else:
                    translatedLines = []

            with open(trans_commit_file_path, 'w', encoding='utf8') as fout, open(commit_file_path,
                                                                                  encoding='utf8') as fin:
                for i, line in enumerate(fin):
                    if i == 0:
                        fout.write(line)
                        continue
                    print(i)
                    if i < len(translatedLines):
                        trans_line = translatedLines[i].strip("\n\t\r")
                        fout.write(trans_line + "\n")
                    else:
                        commit_id, commit_summary, commit_content, commit_time = line.strip("\n\t\r").split(",")
                        translated_commit_summary = translate_intermingual_sentence(commit_summary)
                        translated_commit_content = translate_intermingual_sentence(commit_content)
                        fout.write(
                            "{},{},{},{}\n".format(commit_id, translated_commit_summary, translated_commit_content,
                                                   commit_time))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Github script")
    parser.add_argument("-u", help="user name")
    parser.add_argument("-p", help="password")
    parser.add_argument("-d", help="download path")
    parser.add_argument("-r", nargs="+", help="repo path in github, a list of repo path can be passed")
    parser.add_argument("-t", action="store_true", help="boolean value determine whether do translation")
    args = parser.parse_args()
    for repo_path in args.r:
        print("Processing repo: {}".format(repo_path))
        rpc = RepoCollector(args.u, args.p, args.d, repo_path, args.t)
        rpc.run()
