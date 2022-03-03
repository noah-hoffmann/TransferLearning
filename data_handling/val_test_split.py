from sklearn.model_selection import train_test_split
from glob import glob
import pickle
import gzip as gz
import os
import re
from tqdm import tqdm, trange
import bisect

entries_per_file = 10_000


def get_num_of_entries(files):
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
    data_dir = 'data'
    target_dir = 'split_data'
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    files = sorted(glob(os.path.join(data_dir, '*.pickle.gz')), key=get_num)
    indices = list(range(get_num_of_entries(files)))
    val_indices, test_indices = get_val_test_indices(indices)
    validation_set = []
    test_set = []
    for file in tqdm(files):
        low, high = get_bounds(file)
        data: list = load(file)
        already_done = low * entries_per_file
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
    if not os.path.exists(val_dir):
        os.mkdir(val_dir)
    for i in trange(0, len(validation_set), 10_000):
        save(validation_set[i:i + 10000], os.path.join(val_dir, f'val_data_{i}_{i + 10000}.pickle.gz'))
    test_dir = os.path.join(target_dir, 'test')
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)
    for i in trange(0, len(test_set), 10_000):
        save(test_set[i:i + 10000], os.path.join(test_dir, f'test_data_{i}_{i + 10000}.pickle.gz'))


if __name__ == '__main__':
    main()
