from util import load, get_files
import os
from tqdm import tqdm


def main():
    path = os.path.join('pbe', 'prepared', '*', '*.pickle.gz')
    files = get_files(path)
    ids = set()
    for file in tqdm(files):
        data = load(file)
        for batch_id, in data['batch_ids']:
            ids.add(batch_id)

    to_check = get_files(os.path.join('scan', 'prepared', '*', '*.pickle.gz'))
    # get_files(os.path.join('ps', 'prepared', '*', '*.pickle.gz'))
    total = 0
    remaining = 0
    for file in tqdm(to_check):
        data = load(file)
        total += len(data['batch_ids'])
        for batch_id, in data['batch_ids']:
            if batch_id in ids:
                remaining += 1
    print(f"{remaining} / {total} = {remaining / total:.2%}")


if __name__ == '__main__':
    main()
