from pydriller import Repository
from github import Github
import os

def is_maven_project(repo):
    for file in repo.get_contents(''):
        if file.type == 'file' and file.name == 'pom.xml':
            return True
    return False

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

def find_test_tested_pair(repo, path):
    # traverse through all folders and add all files into a set
    res = []
    file_set = set()
    test_files = repo.get_contents(path + '/test')
    while len(test_files) > 0:
        next_level = []
        for file in test_files:
            if file.type == 'dir':
                next_level.append(file)
            else:
                file_set.add(file.name)
        source_files = next_level
    source_files = repo.get_contents(path + '/main')
    while len(source_files) > 0:
        next_level = []
        for file in source_files:
            if file.type == 'dir':
                next_level.append(file)
            else:
                if file + 'Test.java' in file_set or file + 'Suite.java' in file_set:
                    res.append(file.name)
        source_files = next_level
    return res


REPO_NAME = "apache/spark"
AUTHENTICATOR = os.getenv("AUTHENTICATOR")
g = Github(AUTHENTICATOR)

repo = g.get_repo(REPO_NAME)
print("Mining repo " + REPO_NAME + '.')

if is_maven_project(repo):
    print("Project is maven.")
    paths = find_main_test_dir(repo, "")
    print("Located valid directories with /main and /test folders.")
    for path in paths:
        test_tested_pairs = find_test_tested_pair(repo, path)
        print(test_tested_pairs)