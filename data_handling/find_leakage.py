from util import load, get_files
import os
from tqdm import tqdm


def main():
    path = os.path.join('pbe', 'prepared', '*', '*.pickle.gz')
    files = get_files(path)
    val_test_ids = set()
    for file in tqdm(files):
        data = load(file)
        for batch_id, in data['batch_ids']:
            val_test_ids.add(batch_id)

    train_ids = set()
    for file in tqdm(get_files(os.path.join('pbe', 'prepared', '*.pickle.gz'))):
        data = load(file)
        for batch_id, in data['batch_ids']:
            train_ids.add(batch_id)

    to_check = get_files(os.path.join('scan', 'prepared', '*', '*.pickle.gz'))
    # get_files(os.path.join('ps', 'prepared', '*', '*.pickle.gz'))
    total = 0
    in_val_test = 0
    in_training = 0
    for file in tqdm(to_check):
        data = load(file)
        total += len(data['batch_ids'])
        for batch_id, in data['batch_ids']:
            if batch_id in val_test_ids:
                in_val_test += 1
            elif batch_id in train_ids:
                in_training += 1
    print(f"{in_val_test / total:.2f} are also in pbe test or val set.")
    print(f"{in_training/ total:.2f} are also in pbe training set.")


if __name__ == '__main__':
    main()
