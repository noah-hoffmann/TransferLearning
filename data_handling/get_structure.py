import psycopg2
from getpass import getpass


def main():
    conn = psycopg2.connect(dbname="agm_ht",
                            user="noah",
                            password=getpass())
    cursor = conn.cursor()

    relation = "energy_runs_pbe"

    cursor.execute(f"SELECT structure FROM {relation};")
    for structure, in cursor:
        print(structure)
        break


if __name__ == '__main__':
    main()
