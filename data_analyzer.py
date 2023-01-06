import os
import matplotlib.pyplot as plt
import numpy as np
from util import BUCKET_SIZE, BUCKET_COUNT

# Read data from txt and parse it into a dictionary
def read_data(file):
    res = {}
    try:
        f = open(file, 'r')
        # STEP 1: read the general data
        for i in range(3):
            args = f.readline().split(':')
            res[args[0]] = int(args[1].strip())
        # STEP 2: read data for each interval
        for i in range(BUCKET_COUNT):
            f.readline()
            res["test_before_{}".format(i)] = int(f.readline().split(':')[1].strip())
            res["test_same_{}".format(i)] = int(f.readline().split(':')[1].strip())
            res["test_after_{}".format(i)] = int(f.readline().split(':')[1].strip())
        f.close()
        return res
    except:
        print("Cannot read file", file)
        return res

def calc_frequency(numerator, denominator):
    return np.true_divide(numerator, denominator)

def draw_stacked_freq(data, path):
    labels, test_before, test_same, test_after = [], [], [], []

    for f, d in data.items():
        total = d["test_before"] + d["test_same"] + d["test_after"]
        labels.append(f.strip(".txt"))
        test_before.append(calc_frequency(d["test_before"], total) * 100)
        test_same.append(calc_frequency(d["test_same"], total) * 100)
        test_after.append(calc_frequency(d["test_after"], total) * 100)

    index = np.arange(len(labels))
    bar_width = 0.5
    plt.figure(figsize=(16, 8))
    plt.bar(index, test_before, label="Test Before", width=bar_width)
    plt.bar(index, test_same, bottom=test_before, label="Test Same", width=bar_width)
    plt.bar(index, test_after, bottom=[test_before[i] + test_same[i] for i in range(len(test_same))], label="Test After", width=bar_width)
    plt.xticks(index, labels, fontsize=12)
    plt.ylabel("Percentage", fontsize=15)
    plt.legend()
    plt.savefig(path)

def draw_line_graph(data, path):
    test_before, test_same, test_after = [0] * BUCKET_COUNT, [0] * BUCKET_COUNT, [0] * BUCKET_COUNT
    for i in range(BUCKET_COUNT):
        max_before, max_same, max_after = 0, 0, 0
        for repo in data.values():
            # we ignore the max value
            max_before = max(max_before, repo["test_before_{}".format(i)])
            max_same = max(max_same, repo["test_same_{}".format(i)])
            max_after = max(max_after, repo["test_after_{}".format(i)])
            test_before[i] += repo["test_before_{}".format(i)]
            test_same[i] += repo["test_same_{}".format(i)]
            test_after[i] += repo["test_after_{}".format(i)]
        test_before[i] -= max_before
        test_same[i] -= max_same
        test_after[i] -= max_after

    x = [i * BUCKET_SIZE for i in range(BUCKET_COUNT)]
    plt.figure(figsize=(10, 8))
    plt.plot(x, test_before, label="Test before")
    plt.plot(x, test_same, label="Test same")
    plt.plot(x, test_after, label="Test after")
    plt.xticks(x)
    plt.xlabel("Lines changed")
    plt.ylabel("Number of occurrences")
    plt.legend()
    plt.savefig(path)

# This is only meant for research question 1 now
if __name__ == "__main__":
    # STEP 1: Read and parse data from the data repository
    data = {}
    for file in os.listdir('./data'):
        data[file] = read_data('./data/' + file)
    
    # STEP 2: Plot charts
    draw_stacked_freq(data, './plots/histogram.png')
    # draw_line_graph(data, './plots/line.png')

