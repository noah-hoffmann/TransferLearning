from sklearn.model_selection import train_test_split
from glob import glob
import pickle
import gzip as gz
import os
import re
from tqdm import tqdm, trange
import bisect
import argparse


# entries_per_file = 10_000


def get_num_of_entries(files, entries_per_file):
    num = (len(files) - 1) * entries_per_file
    num += len(
        pickle.load(gz.open(os.path.join(os.path.dirname(files[0]), f'data_{num}_{num + entries_per_file}.pickle.gz'))))
    return num


def get_val_test_indices(indices, val_size=.1, test_size=.1, random_state=0):
    total = val_size + test_size
    _, indices = train_test_split(indices, test_size=total, random_state=random_state)
    val_size = val_size / total
    val, test = train_test_split(indices, train_size=val_size, random_state=random_state)
    return sorted(val), sorted(test)


def load(file):
    return pickle.load(gz.open(file))


def get_files(path):
    return sorted(glob(path), key=get_num)


def save(data, file):
    pickle.dump(data, gz.open(file, 'wb'))


def get_num(file):
    pattern = re.compile(r"data_(\d+)_\d+\.pickle\.gz")
    return int(pattern.search(file).group(1))


def get_bounds(file):
    pattern = re.compile(r"data_(\d+)_(\d+)\.pickle\.gz")
    match = pattern.search(file)
    return int(match.group(1)), int(match.group(2))


def split_indices(indices, upper_bound):
    i = bisect.bisect_left(indices, upper_bound)
    return indices[:i], indices[i:]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', '-d',
                        type=str,
                        default='data')
    parser.add_argument('--target-dir', '-t',
                        type=str,
                        default='split_data')
    parser.add_argument('--entries-per-file', '-e',
                        type=int,
                        default=10_000)
    parser.add_argument('--test-size',
                        type=float,
                        default=0.1)
    parser.add_argument('--val-size',
                        type=float,
                        default=0.1)
    parser.add_argument('--random-state', '-r',
                        type=int,
                        default=0)

    args = parser.parse_args()

    data_dir = args.data_dir
    target_dir = args.target_dir
    entries_per_file = args.entries_per_file

    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    files = get_files(os.path.join(data_dir, '*.pickle.gz'))
    indices = list(range(get_num_of_entries(files, entries_per_file)))
    val_indices, test_indices = get_val_test_indices(indices, args.val_size, args.test_size, args.random_state)
    validation_set = []
    test_set = []
    for file in tqdm(files):
        low, high = get_bounds(file)
        data: list = load(file)
        already_done = low
        if len(val_indices) > 0:
            val, val_indices = split_indices(val_indices, high)
        else:
            val = []
        if len(test_indices) > 0:
            test, test_indices = split_indices(test_indices, high)
        else:
            test = []
        indices = sorted(
            [(i - already_done, validation_set) for i in val] + [(i - already_done, test_set) for i in test],
            reverse=True, key=lambda x: x[0])
        for i, set in indices:
            set.append(data.pop(i))
        save(data, os.path.join(target_dir, os.path.basename(file)))

    val_dir = os.path.join(target_dir, 'val')
    if not os.path.isdir(val_dir):
        os.makedirs(val_dir)
    for i in trange(0, len(validation_set), entries_per_file):
        save(validation_set[i:i + entries_per_file],
             os.path.join(val_dir, f'val_data_{i}_{i + entries_per_file}.pickle.gz'))
    test_dir = os.path.join(target_dir, 'test')
    if not os.path.isdir(test_dir):
        os.makedirs(test_dir)
    for i in trange(0, len(test_set), entries_per_file):
        save(test_set[i:i + entries_per_file],
             os.path.join(test_dir, f'test_data_{i}_{i + entries_per_file}.pickle.gz'))


if __name__ == '__main__':
    main()
