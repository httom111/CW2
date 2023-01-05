import sys
import os
from github import Github
from pydriller import ModificationType
from pydriller import Repository

COMMIT_COUNT = 3000
SMALL_COMMIT = 10
LARGE_COMMIT = 100

def is_test_file(file):
    return file.filename.endswith("Test.java")

def is_tested_file(file):
    return file.filename.endswith(".java")

def parse_test_file_name(file):
    return file[:len(file) - 9]

def parse_tested_file_name(file):
    return file[:len(file) - 5]

def is_maven_project(repo):
    for file in repo.get_contents(''):
        if file.type == 'file' and file.name == 'pom.xml':
            return True
    return False

def parser_commit_size(repo_url):
    repo = Repository(repo_url)
    print("Connected to repo")

    small_commit = 0
    medium_commit = 0
    large_commit = 0

    ctr = 0
    for commit in repo.traverse_commits():
        if commit.lines < SMALL_COMMIT:
            small_commit += 1
        elif commit.lines < LARGE_COMMIT:
            medium_commit += 1
        else:
            large_commit += 1
        ctr += 1
        # if ctr > COMMIT_COUNT:
        #     break
    print("small_commit: %d" % small_commit)
    print("medium_commit: %d" % medium_commit)
    print("large_commit: %d" % large_commit)

def parser_main(repo_url):
    repo = Repository(repo_url)
    print("Connected to repo")

    total_commit = 0
    commit_with_test_class = 0
    commits = {}
    test_classes = {}
    tested_classes = {}
    modified_files_sum = 0
    modified_lines_sum = 0

    ctr = 1
    for commit in repo.traverse_commits():
        # question 1 & 3
        print("Traversing commit " + commit.hash + ", count: " + str(ctr), end='\r')
        ctr += 1
        has_test_class = 0
        try:
            commit.modified_files
        except ValueError:
            print("\nUnable to access commit", commit.hash)
            continue

        commits[commit.hash] = (commit.committer_date.timestamp(), commit.lines)

        for file in commit.modified_files:
            # change_type == ModificationType.ADDED
            # what if the filename/path has changed?
            if file.change_type == ModificationType.ADD:
                if is_test_file(file):
                    # we should store the full path of the file
                    file_without_extension = file.filename[0:len(file.filename) - 9]
                    has_test_class = True
                    if test_classes.get(file_without_extension) is None:
                        test_classes[file_without_extension] = commit.hash
                elif is_tested_file(file):
                    file_without_extension = file.filename[0:len(file.filename) - 5]
                    if tested_classes.get(file_without_extension) is None:
                        tested_classes[file_without_extension] = commit.hash
            elif file.change_type == ModificationType.RENAME and file.old_path is not None:
                # check if the original file exists
                if is_test_file(file):
                    # parse the old name of the file
                    # check if the file exists in the path
                    old_file_name = file.old_path.split('/')[-1]
                    old_file_without_extension = parse_test_file_name(old_file_name)
                    new_file_without_extension = parse_test_file_name(file.filename)
                    if test_classes.get(old_file_without_extension) is not None:
                        test_classes[new_file_without_extension] = test_classes[old_file_without_extension]
                        del test_classes[old_file_without_extension]
                    else:
                        test_classes[new_file_without_extension] = commit.hash
                elif is_tested_file(file):
                    old_file_name = file.old_path.split('/')[-1]
                    old_file_without_extension = parse_tested_file_name(old_file_name)
                    new_file_without_extension = parse_tested_file_name(file.filename)
                    if test_classes.get(old_file_without_extension) is not None:
                        test_classes[new_file_without_extension] = test_classes[old_file_without_extension]
                        del test_classes[old_file_without_extension]
                    else:
                        test_classes[new_file_without_extension] = commit.hash
            elif file.change_type == ModificationType.DELETE:
                if is_test_file(file):
                    file_without_extension = parse_test_file_name(file.filename)
                    if test_classes.get(file_without_extension) is not None:
                        del test_classes[file_without_extension]
                elif is_tested_file(file):
                    file_without_extension = parse_tested_file_name(file.filename)
                    if tested_classes.get(file_without_extension) is not None:
                        del tested_classes[file_without_extension]

        if has_test_class:
            commit_with_test_class += 1
        # question 2
        modified_files_sum += len(commit.modified_files)
        modified_lines_sum += commit.lines
        total_commit += 1
        # if total_commit >= COMMIT_COUNT:
        #     break
    print("", end='\r')
    print("total_commit: %d" % total_commit)
    print("commit_with_test_class: %d" % commit_with_test_class)
    print("test_classes_count: %d" % len(test_classes))
    print("tested_classes_count: %d" % len(tested_classes))
    print("modified_files_avg: %d, modified_lines_avg: %d" % (modified_files_sum / total_commit, modified_lines_sum / total_commit))

    test_before_count = [0, 0, 0]
    test_same_count = [0, 0, 0]
    test_after_count = [0, 0, 0]
    test_without_class = 0
    for test_class_name in test_classes.keys():
        if tested_classes.get(test_class_name) is None:
            test_without_class += 1
        else:
            cmt = commits.get(test_classes[test_class_name])
            # question 2
            if cmt[1] < SMALL_COMMIT:
                index = 0
            elif cmt[1] < LARGE_COMMIT:
                index = 1
            else:
                index = 2

            t1 = commits.get(test_classes[test_class_name])[0]
            t2 = commits.get(tested_classes[test_class_name])[0]
            if t1 < t2:
                test_before_count[index] += 1
            elif t1 == t2:
                test_same_count[index] += 1
            else:
                test_after_count[index] += 1

    print("test_without_tested_class: %d, tested_class_without_test: %d"
          % (test_without_class, len(tested_classes) - len(test_classes)))

    for i in range(3):
        print(
            "commit size: %d, test_before_count: %d, test_same_count: %d, test_after_count: %d"
            % (i, test_before_count[i], test_same_count[i], test_after_count[i]))

    # for c in commits.keys():
    #     print("hash: %s, timestamp: %d, lines: %d" % (c, commits.get(c)[0], commits.get(c)[1]))

    return (test_before_count, test_same_count, test_after_count)

if __name__ == '__main__':
    repos = sys.argv[1:]
    if len(repos) == 0:
        print("Please supply the argument with repo names")
        exit(1)
    for repo_name in sys.argv[1:]:
        repo_url = "https://github.com/" + repo_name

        print("Mining repo " + repo_name)
        # check if POM.xml exists in the folder
        AUTHENTICATOR = os.getenv("AUTHENTICATOR")
        repo = Github(AUTHENTICATOR).get_repo(repo_name)
        if not is_maven_project(repo):
            print("Not maven: POM.xml not discovered")
            continue
        print("Project is using maven")

        # parser_commit_size(repo_url)

        (test_before_count, test_same_count, test_after_count) = parser_main(repo_url)

        file_name = repo_name.split('/')[1]
        f = open("data/" + file_name + '.txt', "w")
        f.writelines(["test_before:" + str(test_before_count[0] + test_before_count[1] + test_before_count[2])
                      + '\n', "test_same:" + str(test_same_count[0] + test_same_count[1] + test_same_count[2])
                      + '\n', "test_after:" + str(test_after_count[0] + test_after_count[1] + test_after_count[2])
                      + "\n"])
        for i in range(3):
            f.writelines(["commit_size:" + str(i)
                          + "\ntest_before:" + str(test_before_count[i])
                          + "\ntest_same:" + str(test_same_count[i])
                          + "\ntest_after:" + str(test_after_count[i])
                          + "\n"])
        f.close()
        print()
