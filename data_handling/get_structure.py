from util import connect
from pymatgen.entries.computed_entries import ComputedStructureEntry
from pymatgen.core.structure import Structure, Composition
import pickle
import gzip as gz
import os
from tqdm import tqdm
from correct_e_phase_separation import find_all_affected_compositions, get_compositions
from getpass import getpass


def main():
    password = getpass()
    main_cursor = connect(password=password)
    side_cursor = connect(password=password)

    relation = "energy_runs_pbe"
    condition = "e_phase_separation is not NULL"
    data_dir = 'data'
    entries_per_file = 10_000

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    # find all compositions, which have wrong e_phase_separation values
    affected_formulas = find_all_affected_compositions(main_cursor)

    main_cursor.execute(f"SELECT COUNT(*) FROM {relation} WHERE {condition};")
    total, = main_cursor.fetchone()

    main_cursor.execute(f"SELECT structure, mat_id, formula, energy_corrected, e_form, e_above_hull, spg, e_phase_separation "
                   f"FROM {relation} "
                   f"WHERE {condition} "
                   f"ORDER BY mat_id;")
    entries = []
    i = 0
    for structure, mat_id, formula, energy_corrected, e_form, e_above_hull, spg, e_phase in tqdm(main_cursor, total=total):
        if formula in affected_formulas:
            print(f'\n{formula}')
            e_phase = get_compositions(formula, side_cursor).at[mat_id, 'e_phase_separation']
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
            with gz.open(os.path.join(data_dir, f'data_{i}_{i + entries_per_file}.pickle.gz', 'wb')) as file:
                pickle.dump(entries, file)
                i += entries_per_file
            entries.clear()
            exit()


if __name__ == '__main__':
    main()
