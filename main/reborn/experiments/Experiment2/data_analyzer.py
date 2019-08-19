# measure the characters of the data to find out in which cases gvsm is better than translation
import os, re

from DataReader import GtiProjectReader


def en_zh_ratio(docs: dict):
    en_cnt = 0
    zh_cnt = 0
    for doc_id in docs.keys():
        doc = docs[doc_id]
        tokens = doc.split()
        for token in tokens:
            match_res = re.match("[a-zA-Z0-9]+", token)
            if match_res!=None and len(match_res.group()) == len(token):
                en_cnt += 1
            else:
                zh_cnt += 1
    return en_cnt, zh_cnt


if __name__ == "__main__":
    git_project_root = "G:\\Projects\\InterLingualTrace\\main\\reborn\\github_project_crawl\\git_projects"
    groups = os.listdir(git_project_root)
    project_title = [""]
    analyz_data = {}

    for group_name in groups:
        group_dir = os.path.join(git_project_root, group_name)
        projects = os.listdir(group_dir)
        for project_name in projects:
            repo_path = os.path.join(group_name, project_name)
            reader = GtiProjectReader(repo_path)

            origin_dataset = reader.readData(False)
            dataSet, dataset_info = reader.limit_artifacts_in_links(origin_dataset, origin_dataset)
            print(dataset_info)
            project_title.append(project_name)
            for link_set_id in dataSet.gold_link_sets:
                link_set = dataSet.gold_link_sets[link_set_id]
                source_artif = link_set.artiPair.source_artif
                target_artif = link_set.artiPair.target_artif
                links = link_set.links
                s_en_cnt, s_zh_cnt = en_zh_ratio(source_artif)
                t_en_cnt, t_zh_cnt = en_zh_ratio(target_artif)
                s_token_num = s_en_cnt + s_zh_cnt
                t_token_num = t_en_cnt + t_zh_cnt
                total_token_num = s_token_num + t_token_num

                analyz_data.setdefault("link_num", []).append(len(links))
                analyz_data.setdefault("source_num", []).append(len(source_artif))
                analyz_data.setdefault("target_num", []).append(len(target_artif))
                analyz_data.setdefault("source_en_token_num", []).append(s_en_cnt)
                analyz_data.setdefault("source_zh_token_num", []).append(s_zh_cnt)
                analyz_data.setdefault("source_zh_ratio", []).append(
                    round(s_zh_cnt / s_token_num, 4) if s_token_num > 0 else 0)
                analyz_data.setdefault("target_en_token_num", []).append(t_en_cnt)
                analyz_data.setdefault("target_zh_token_num", []).append(t_zh_cnt)
                analyz_data.setdefault("target_zh_ratio", []).append(
                    round(t_zh_cnt / t_token_num, 4) if t_token_num > 0 else 0)
                analyz_data.setdefault("total_tokens", []).append(total_token_num)
                analyz_data.setdefault("total_zh_ratio", []).append(
                    round((s_zh_cnt + t_zh_cnt) / total_token_num, 4) if total_token_num > 0 else 0)

    with open("results/data_status.csv", "w", encoding='utf8') as fout:
        fout.write(",".join(project_title) + "\n")
        for attrib in analyz_data.keys():
            data_row = analyz_data[attrib]
            data_row.insert(0, attrib)
            data_row = [str(x) for x in data_row]
            fout.write(",".join(data_row) + "\n")
