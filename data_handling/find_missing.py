from util import connect, save, load, get_files
from pymatgen.entries.computed_entries import ComputedStructureEntry
import argparse
from tqdm import tqdm
import os.path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', '-d',
                        type=str)
    parser.add_argument('--relation', '-r')

    args = parser.parse_args()

    # find files
    files = get_files(os.path.join(args.data_dir, '*.pickle.gz'))

    # connect to database
    cursor = connect()

    # sql query
    query = "SELECT mat_id FROM {relation} WHERE mat_id = '{mat_id}';"

    total = 0
    missing = 0
    for file in tqdm(files):
        data: list[ComputedStructureEntry] = load(file)
        for entry in data:
            total += 1
            mat_id = entry.data['id']
            cursor.execute(query.format(relation=args.relation, mat_id=mat_id))
            results = cursor.fetchall()
            if len(results) == 0:
                missing += 1
    print(f"{missing} / {total} are missing. ({missing / total:.2%})")


if __name__ == '__main__':
    main()
