from util import connect
from pymatgen.entries.computed_entries import ComputedStructureEntry
from pymatgen.core.structure import Structure, Composition
import pickle
import gzip as gz
import os
from tqdm import tqdm
from correct_e_phase_separation import find_all_affected_compositions, get_compositions
from getpass import getpass
import warnings
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--relation', '-r',
                        type=str,
                        default='energy_runs_pbe')
    parser.add_argument('--data-dir', '-d',
                        type=str,
                        default='data')
    parser.add_argument('--condition', '-c',
                        type=str,
                        default='e_above_hull is not NULL')
    parser.add_argument('--entries-per-file', '-e',
                        type=int,
                        default=10_000)

    args = parser.parse_args()

    password = getpass()
    main_cursor = connect(password=password)
    side_cursor = connect(password=password)

    relation = args.relation
    condition = args.condition
    data_dir = args.data_dir
    entries_per_file = args.entries_per_file

    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)

    # find all compositions, which have wrong e_phase_separation values
    affected_formulas = find_all_affected_compositions(main_cursor, relation)

    main_cursor.execute(f"SELECT COUNT(*) FROM {relation} WHERE {condition};")
    total, = main_cursor.fetchone()

    main_cursor.execute(
        f"SELECT structure, mat_id, formula, energy_corrected, e_form, e_above_hull, spg, e_phase_separation "
        f"FROM {relation} "
        f"WHERE {condition} "
        f"ORDER BY mat_id;")
    entries = []
    i = 0
    for structure, mat_id, formula, energy_corrected, e_form, e_above_hull, spg, e_phase in tqdm(main_cursor,
                                                                                                 total=total):
        if formula in affected_formulas:
            try:
                e_phase = get_compositions(formula, side_cursor, relation).at[mat_id, 'e_phase_separation']
            except KeyError:
                warnings.warn(
                    f"Caught KeyError for {mat_id=} and {formula=} in file data_{i}_{i + entries_per_file}.pickle.gz!")
        entry = Structure.from_dict(structure)
        data = {
            'id': mat_id,
            'e-form': e_form,
            'e_above_hull': e_above_hull,
            'decomposition': formula,
            'spg': spg,
            'volume': entry.volume / entry.num_sites,
            'e_above_hull_new': e_phase
        }
        entry = ComputedStructureEntry(entry, energy_corrected, composition=Composition(formula), data=data,
                                       entry_id=mat_id)
        entries.append(entry)
        if len(entries) >= entries_per_file:
            with gz.open(os.path.join(data_dir, f'data_{i}_{i + entries_per_file}.pickle.gz'), 'wb') as file:
                pickle.dump(entries, file)
                i += entries_per_file
            entries.clear()
    if len(entries) > 0:
        with gz.open(os.path.join(data_dir, f'data_{i}_{i + entries_per_file}.pickle.gz'), 'wb') as file:
            pickle.dump(entries, file)
            i += entries_per_file
        entries.clear()


if __name__ == '__main__':
    main()
