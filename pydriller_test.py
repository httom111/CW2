import sys
from pydriller import ModificationType
from pydriller import Repository

total_commit = 0
commit_with_test_class = 0
test_classes = {}
tested_classes = {}
modified_files_sum = 0
modified_lines_sum = 0
for commit in Repository(sys.argv[1]).traverse_commits():
    # question 1 & 3
    has_test_class = 0
    for file in commit.modified_files:
        if file.change_type != ModificationType.DELETE and file.change_type != ModificationType.UNKNOWN:
            if file.filename.endswith("Test.java"):
                file_name_without_extension = file.filename[0:len(file.filename) - 9]
                has_test_class = True
                if test_classes.get(file_name_without_extension) is None:
                    test_classes[file_name_without_extension] = commit.committer_date.timestamp()
            elif file.filename.endswith(".java"):
                file_name_without_extension = file.filename[0:len(file.filename) - 5]
                if tested_classes.get(file_name_without_extension) is None:
                    tested_classes[file_name_without_extension] = commit.committer_date.timestamp()
    if has_test_class:
        commit_with_test_class += 1
    # question 2
    modified_files_sum += len(commit.modified_files)
    modified_lines_sum += commit.lines
    total_commit += 1
    # if total_commit >= 100:
    #     break

print("total_commit: %d" % total_commit)
print("commit_with_test_class: %d" % commit_with_test_class)
print("test_classes_count: %d" % len(test_classes))
print("tested_classes_count: %d" % len(tested_classes))
print("modified_files_avg: %d, modified_lines_avg: %d" % (modified_files_sum / total_commit, modified_lines_sum / total_commit))

test_before_count = 0
test_same_count = 0
test_after_count = 0
test_without_class = 0
for test_class_name in test_classes.keys():
    if tested_classes.get(test_class_name) is None:
        test_without_class += 1
    else:
        t1 = test_classes.get(test_class_name)
        t2 = tested_classes.get(test_class_name)
        if t1 < t2:
            test_before_count += 1
        elif t1 == t2:
            test_same_count += 1
        else:
            test_after_count += 1

print(
    "test_before_count: %d, test_same_count: %d, test_after_count: %d, test_without_class: %d, tested_class_without_test: %d"
    % (test_before_count, test_same_count, test_after_count, test_without_class,
       len(tested_classes) - len(test_classes)))
