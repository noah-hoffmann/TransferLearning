from util import load, get_files, remove_batch_ids, save
import os
from tqdm import tqdm


def main():
    path = os.path.join('scan', 'prepared', '*', '*.pickle.gz')
    files = get_files(path)
    val_test_ids = set()
    for file in tqdm(files):
        data = load(file)
        for batch_id, in data['batch_ids']:
            val_test_ids.add(batch_id)

    to_check = get_files(os.path.join('pbe', 'prepared', '*.pickle.gz'))
    for file in tqdm(to_check):
        data = load(file)
        to_remove = set()
        for batch_id, in data['batch_ids']:
            if batch_id in val_test_ids:
                to_remove.add(batch_id)
        remove_batch_ids(data, to_remove)
        save(data, file)


if __name__ == '__main__':
    main()
