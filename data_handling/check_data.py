from glob import glob
import os
import pickle
import gzip as gz
from pymatgen.entries.computed_entries import ComputedStructureEntry
from tqdm import tqdm
from util import connect


def is_fixable(mat_id, cursor):
    query = 'SELECT e_above_hull ' \
            'FROM energy_runs_pbe ' \
            'WHERE mat_id = {mat_id};'
    cursor.execute(query.format(mat_id=mat_id))
    result, = cursor.fetchone()
    return False if result is None else True


def main():
    data_dir = 'data'
    files = glob(os.path.join(data_dir, '*.pickle.gz'))
    total = 0
    missing = 0
    fixable = 0
    cursor = connect()
    for file in tqdm(files):
        with gz.open(file) as f:
            data: list[ComputedStructureEntry] = pickle.load(f)
        total += len(data)
        for entry in data:
            if entry.data['e_above_hull'] is None:
                missing += 1
                if is_fixable(entry.data['id'], cursor):
                    fixable += 1
    print(f'There are {missing} / {total} missing e_above_hull values!')
    print(f'{fixable} can be fixed.')


if __name__ == '__main__':
    main()
