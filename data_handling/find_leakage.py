from util import load, get_files
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
    total = 0
    to_delete = 0
    for file in tqdm(to_check):
        data = load(file)
        total += len(data['batch_ids'])
        for batch_id, in data['batch_ids']:
            if batch_id in val_test_ids:
                to_delete += 1
    print(f"{to_delete / total:.2%} needs to be removed.")


if __name__ == '__main__':
    main()
