from val_test_split import get_files
import os
from tqdm import tqdm
from util import remove_batch_ids, load, save
import re
from itertools import chain
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p',
                        type=str,
                        default=os.path.join("pbe", "prepared"))

    args = parser.parse_args()
    paths = [os.path.join(args.path, '*.pickle.gz'), os.path.join(args.path, '*', '*.pickle.gz')]
    files = list(chain(*[get_files(path) for path in paths]))
    single_atom_comp = re.compile(r'^[A-Z][a-z]*\d+$')
    for file in tqdm(files):
        data = load(file)
        ids_to_remove = set()
        for (batch_id,), (batch_comp,) in zip(data['batch_ids'], data['batch_comp']):
            if single_atom_comp.match(batch_comp):
                ids_to_remove.add(batch_id)
        remove_batch_ids(data, ids_to_remove)
        save(data, file)


if __name__ == '__main__':
    main()
