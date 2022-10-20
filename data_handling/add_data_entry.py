from util import connect, save, load, get_files
from pymatgen.entries.computed_entries import ComputedStructureEntry
import argparse
from tqdm import tqdm
import warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', '-d',
                        type=str)
    parser.add_argument('--property', '-p')
    parser.add_argument('--relation', '-r')

    args = parser.parse_args()

    # find files
    files = get_files(args.data_dir)

    # connect to database
    cursor = connect()

    # sql query
    query = "SELECT {property} FROM {relation} WHERE mat_id = {mat_id};"

    for file in tqdm(files):
        data: list[ComputedStructureEntry] = load(file)
        for entry in data:
            mat_id = entry.data['id']
            cursor.execute(query.format(property=args.property, relation=args.relation, mat_id=mat_id))
            results = cursor.fetchall()
            if len(results) == 0:
                warnings.warn(f"{mat_id = } does not exist in database, skipping this entry!")
                continue
            elif len(results) > 1:
                warnings.warn(f"{mat_id = } not unique, only using first result!")
            entry.data[args.property] = results[0][0]
        save(data, file)


if __name__ == '__main__':
    main()
