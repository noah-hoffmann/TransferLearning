from glob import glob
import os
import pickle
import gzip as gz
from pymatgen.entries.computed_entries import ComputedStructureEntry
from tqdm import tqdm


def main():
    data_dir = 'data'
    files = glob(os.path.join(data_dir, '*.pickle.gz'))
    for file in tqdm(files):
        with gz.open(file) as f:
            data: list[ComputedStructureEntry] = pickle.load(f)
        for entry in data:
            if entry.data['e_above_hull'] is None:
                print(f"\n Entry in file {file!r} with mat_id {entry.data['id']!r} has missing 'e_above_hull'!")


if __name__ == '__main__':
    main()
