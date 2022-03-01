from util import connect
from pymatgen.entries.computed_entries import ComputedStructureEntry
from pymatgen.core.structure import Structure, Composition
import pickle
import gzip as gz
import os
from tqdm import tqdm


def main():
    cursor = connect()

    relation = "energy_runs_pbe"
    data_dir = 'data'
    entries_per_file = 10_000

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    cursor.execute(f"SELECT COUNT(*) FROM {relation} WHERE e_above_hull is not NULL;")
    total, = cursor.fetchone()

    cursor.execute(f"SELECT structure, mat_id, formula, energy_corrected, e_form, e_above_hull, spg, e_phase_separation FROM {relation}"
                   f"WHERE e_above_hull is not NULL"
                   f"ORDER BY mat_id;")
    entries = []
    i = 0
    for structure, mat_id, formula, energy_corrected, e_form, e_above_hull, spg, e_phase in tqdm(cursor, total=total):
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


if __name__ == '__main__':
    main()
