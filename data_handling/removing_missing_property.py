from tqdm import tqdm
from glob import glob
import os.path
from argparse import ArgumentParser
from util import load, save
from pymatgen.entries.computed_entries import ComputedStructureEntry


def main():
    parser = ArgumentParser()
    parser.add_argument('--data-dir', '-d')
    parser.add_argument('--property', '-p')

    args = parser.parse_args()

    files = glob(os.path.join(args.data_dir, '*.pickle.gz')) + glob(os.path.join(args.data_dir, '*', '*.pickle.gz'))

    removed = 0
    for file in tqdm(files):
        data: list[ComputedStructureEntry] = load(file)
        to_remove = []
        for i, entry in enumerate(data):
            if args.property not in entry.data:
                to_remove.append(i)

        for i in reversed(to_remove):
            data.pop(i)
        removed += len(to_remove)
        save(data, file)
    print(f"{removed} entries were removed!")


if __name__ == '__main__':
    main()
