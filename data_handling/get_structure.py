import psycopg2
from getpass import getpass
from pymatgen.entries.computed_entries import ComputedStructureEntry
from pymatgen.core.structure import Structure, Composition
import pickle
import gzip as gz
import os
from tqdm import trange, tqdm


def main():
    conn = psycopg2.connect(dbname="agm_ht",
                            user="noah",
                            password=getpass())
    cursor = conn.cursor()

    relation = "energy_runs_pbe"

    cursor.execute(f"SELECT structure, mat_id, formula, energy_corrected, e_form, e_above_hull, spg FROM {relation};")
    entries = []
    for structure, mat_id, formula, energy_corrected, e_form, e_above_hull, spg in tqdm(cursor):
        entry = Structure.from_dict(structure)
        data = {
            'id': mat_id,
            'e-form': e_form,
            'e_above_hull': e_above_hull,
            'decomposition': formula,
            'spg': spg,
            'volume': entry.volume / entry.num_sites
        }
        entry = ComputedStructureEntry(entry, energy_corrected, composition=Composition(formula), data=data,
                                       entry_id=mat_id)
        entries.append(entry)
    entries_per_file = 10_000
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    for i in trange(0, len(entries), entries_per_file):
        with gz.open(os.path.join(data_dir, f'data_{i}_{i + entries_per_file}.pickle.gz', 'wb')) as file:
            pickle.dump(entries[i: i + entries_per_file], file)


if __name__ == '__main__':
    main()
