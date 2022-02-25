import psycopg2
from getpass import getpass
# from pymatgen.entries.computed_entries import ComputedStructureEntry
from pymatgen.core.structure import Structure


def main():
    conn = psycopg2.connect(dbname="agm_ht",
                            user="noah",
                            password=getpass())
    cursor = conn.cursor()

    relation = "energy_runs_pbe"

    cursor.execute(f"SELECT structure FROM {relation};")
    for structure, in cursor:
        entry = Structure.from_dict(structure)
        print(entry)
        break


if __name__ == '__main__':
    main()
