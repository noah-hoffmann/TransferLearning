from glob import glob
import os
import pickle
import gzip as gz
from pymatgen.entries.computed_entries import ComputedStructureEntry
from tqdm import tqdm


def main():
    data_dir = 'data'
    files = glob(os.path.join(data_dir, '*.pickle.gz'))
    total = 0
    missing = 0
    for file in tqdm(files):
        with gz.open(file) as f:
            data: list[ComputedStructureEntry] = pickle.load(f)
        total += len(data)
        for entry in data:
            if entry.data['e_above_hull'] is None:
                missing += 1
    print(f'There are {missing} / {total} missing e_above_hull values!')


if __name__ == '__main__':
    main()
