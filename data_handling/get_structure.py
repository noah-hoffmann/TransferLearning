import psycopg2
from getpass import getpass
from pymatgen.entries.computed_entries import ComputedStructureEntry
from pymatgen.core.structure import Structure, Composition


def main():
    conn = psycopg2.connect(dbname="agm_ht",
                            user="noah",
                            password=getpass())
    cursor = conn.cursor()

    relation = "energy_runs_pbe"

    cursor.execute(f"SELECT structure, mat_id, formula, energy_corrected, e_form, e_above_hull FROM {relation};")
    for structure, mat_id, formula, energy_corrected, e_form, e_above_hull in cursor:
        entry = Structure.from_dict(structure)
        data = {
            'e-form': e_form,
            'e_above_hull': e_above_hull,
            'decomposition': formula
        }
        entry = ComputedStructureEntry(entry, energy_corrected, composition=Composition(formula), data=data)
        print(entry)
        break


if __name__ == '__main__':
    main()
