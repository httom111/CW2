import os
import matplotlib.pyplot as plt
import numpy as np
from util import BUCKET_SIZE, BUCKET_COUNT

# Read data from txt and parse it into a dictionary
def read_data(file):
    try:
        f = open(file, 'r')
        res = {}
        for line in f.readlines():
            args = line.split(':')
            res[args[0]] = int(args[1].strip())
        f.close()
        return res
    except:
        print("Cannot read file", file)
        return None

def calc_frequency(numerator, denominator):
    return np.true_divide(numerator, denominator)

# This is only meant for research question 1 now
if __name__ == "__main__":
    # STEP 1: Read and parse data from the data repository
    data = {}
    for file in os.listdir('./data'):
        data[file] = read_data('./data/' + file)

    # STEP 2: For each piece of data, draw on the plot
    labels, test_before, test_same, test_after = [], [], [], []

    for f, d in data.items():
        total = 0
        for v in d.values():
            total += v
        labels.append(f)
        test_before.append(calc_frequency(d["test_before"], total) * 100)
        test_same.append(calc_frequency(d["test_same"], total) * 100)
        test_after.append(calc_frequency(d["test_after"], total) * 100)

    index = np.arange(len(labels))
    bar_width = 0.5
    plt.figure(figsize=(20, 20))
    plt.bar(index, test_before, label="Test Before", width=bar_width)
    plt.bar(index, test_same, bottom=test_before, label="Test Same", width=bar_width)
    plt.bar(index, test_after, bottom=[test_before[i] + test_same[i] for i in range(len(test_same))], label="Test After", width=bar_width)
    plt.xticks(index, labels)
    # STEP 3: Output the plot
    plt.savefig('./plots/histogram.png')