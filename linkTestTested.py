from pydriller import Repository
from github import Github
import os
import time

"""
    STEP 1 
    Determine if a project is a maven project.
    We achieve this by finding whether a pom.xml file exists at root directory
"""
def is_maven_project(repo):
    for file in repo.get_contents(''):
        if file.type == 'file' and file.name == 'pom.xml':
            return True
    return False

"""
    STEP 2
    Run depth first search and traverse through all subdirectories.
    Return directories that have 'main' and 'test'.
"""
def find_main_test_dir(repo, path):
    res = []
    has_main = False
    has_test = False
    for file in repo.get_contents(path):
        if file.type == 'dir':
            res.extend(find_main_test_dir(repo, file.path))
            if file.name == 'main':
                has_main = True
            elif file.name == 'test':
                has_test = True
    if has_main and has_test:
        res.append(path)
    return res

"""
    STEP 3
    For each valid directory retrieved from step 2.
    Run breadth first search on both 'main' and 'test' folder
    Check if there exists test file that ends with ClassNameTest.java
"""
def find_test_tested_pair(repo, path):
    # traverse through all folders and add all files into a set
    res, paths = [], [path + '/test']
    file_set = set()
    count = 0
    while len(paths) > 0:
        new_paths = []
        for p in paths:
            test_files = repo.get_contents(p)
            for file in test_files:
                if file.type == 'dir':
                    new_paths.append(file.path)
                else:
                    count += 1
                    file_set.add(file.name)
                    print("File count:", count)

        paths = new_paths
    paths = [path + '/main']
    while len(paths) > 0:
        new_paths = []
        for p in paths:
            source_files = repo.get_contents(p)
            for file in source_files:
                if file.type == 'dir':
                    new_paths.append(file.path)
                else:
                    if file.name[:-5] + 'Test.java' in file_set or file.name + 'Suite.java' in file_set:
                        res.append(file.name)
                    count += 1
                    print("File count:", count)
        paths = new_paths
    return res

if __name__ == '__main__':
    REPO_NAME = "apache/flink"
    AUTHENTICATOR = os.getenv("AUTHENTICATOR")
    g = Github(login_or_token=AUTHENTICATOR, per_page=100)

    repo = g.get_repo(REPO_NAME)
    print("Mining repo " + REPO_NAME + '.')

    if is_maven_project(repo):
        print("Project is maven.")
        paths = find_main_test_dir(repo, "flink-clients/src")
        # paths = ["flink-connectors/flink-connector-aws-base/src"]
        print("Located valid directories with /main and /test folders.")
        for path in paths:
            test_tested_pairs = find_test_tested_pair(repo, path)
            print(test_tested_pairs)