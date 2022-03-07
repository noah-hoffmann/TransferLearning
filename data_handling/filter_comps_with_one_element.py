
from val_test_split import get_files
import os
from tqdm import tqdm
from util import remove_batch_ids, load, save
import re


def main():
    paths = os.path.join('pbe', 'prepared', '*.pickle.gz')
    files = get_files(paths)
    single_atom_comp = re.compile(r'^[A-Z][a-z]*\d+$')
    for file in tqdm(files):
        data = load(file)
        ids_to_remove = []
        for (batch_id,), (batch_comp,) in zip(data['batch_ids'], data['batch_comp']):
            if single_atom_comp.match(batch_comp):
                print(batch_id, batch_comp)


if __name__ == '__main__':
    main()
