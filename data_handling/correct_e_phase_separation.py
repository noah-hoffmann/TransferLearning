from util import connect
import pandas as pd


def main():
    cursor = connect()
    formulas = find_all_affected_compositions(cursor)
    print(formulas[:10])
    comp = get_compositions(formulas[0], cursor)
    print(comp)
    correct_composition(comp)
    print(comp)
    update_table(comp, cursor)


def find_all_affected_compositions(cursor):
    query = "SELECT DISTINCT formula " \
            "FROM energy_runs_pbe " \
            "WHERE e_above_hull > 0 AND e_above_hull <> e_phase_separation " \
            "ORDER BY formula"

    cursor.execute(query)
    formulas = cursor.fetchall()
    return [f[0] for f in formulas]


def get_compositions(formula, cursor):
    query = f"SELECT mat_id, energy_corrected, e_phase_separation, nsites FROM " \
            f"energy_runs_pbe " \
            f"WHERE formula='{formula}';"
    cursor.execute(query)
    results = pd.DataFrame(cursor.fetchall(), columns=['mat_id', 'energy_corrected', 'e_phase_separation', 'nsites'])
    return results


def correct_composition(compositions: pd.DataFrame):
    # Sort compositions by energy per atom
    compositions['energy_per_atom'] = compositions['energy_corrected'] / compositions['nsites']
    compositions.sort_values(by='energy_per_atom', ignore_index=True, inplace=True)
    # if all distances to the convex hull are greater than zero, nothing needs to be changed
    if compositions.at[0, 'e_phase_separation'] > 0:
        return compositions
    stable_energy_per_atom = compositions.at[0, 'energy_per_atom']
    # if more than 2 compounds had a negative distance, the most stable one also needs to be corrected
    if compositions.at[1, 'e_phase_separation'] < 0:
        compositions.at[0, 'e_phase_separation'] = stable_energy_per_atom - compositions.at[1, 'energy_per_atom']

    # correct all other distances to the convex hull by calculating their energetic distance (per atom) to the most stable compound
    for i in range(1, len(compositions)):
        compositions.at[i, 'e_phase_separation'] = compositions.at[i, 'energy_per_atom'] - stable_energy_per_atom
    return compositions


def update_table(corrected_compostion: pd.DataFrame, cursor):
    query_format = "UPDATE energy_runs_pbe " \
                   "SET e_phase_separation = {e_phase_separation} " \
                   "WHERE mat_id = {mat_id}"
    for _, row in corrected_compostion.iterrows():
        query = query_format.format(e_phase_separation=row['e_phase_separation'],
                                    mat_id=row['mat_id'])
        print(query)
        # First check if everything is correct
        # cursor.execute(query)


def test_correcting():
    Ac2AgHg = pd.DataFrame([(-0.000970758, -12.8615, 4),
                            (-0.00046, -12.8595, 4),
                            (0.00040276, -12.856, 4)], columns=['e_phase_separation', 'energy_corrected', 'nsites'])
    print(correct_composition(Ac2AgHg))
    LuF3 = pd.DataFrame([(-4.53112, -53.8143, 8),
                         (-4.37892, -52.5967, 8),
                         (-4.53174, -26.9096, 4),
                         (-4.35039, -26.1842, 4),
                         (-4.10307, -25.1949, 4),
                         (-4.08355, -25.1169, 4)], columns=['e_phase_separation', 'energy_corrected', 'nsites'])
    print(correct_composition(LuF3))
    ScNi = pd.DataFrame([(-0.0616423, -52.504, 8),
                         (-0.0511331, -52.420, 8),
                         (0.139964, -50.892, 8),
                         (-0.0598753, -39.368, 6),
                         (-0.0641008, -26.262, 4),
                         (-0.0587164, -26.240, 4),
                         (-0.0408912, -26.169, 4),
                         (-0.0659847, -13.134, 2),
                         (-0.0577912, -13.118, 2),
                         (-0.0574816, -13.117, 2),
                         (-0.0570807, -13.117, 2),
                         (-0.0511756, -13.105, 2),
                         (-0.0507933, -13.104, 2),
                         (-0.0506307, -13.104, 2),
                         (-0.050628, -13.104, 2),
                         (-0.05062, -13.104, 2),
                         (-0.05062, -13.104, 2),
                         (-0.0506179, -13.104, 2),
                         (-0.050618, -13.104, 2),
                         (-0.0506179, -13.104, 2),
                         (-0.0506173, -13.104, 2),
                         (-0.0506171, -13.104, 2),
                         (-0.0506149, -13.104, 2),
                         (-0.0506153, -13.104, 2),
                         (-0.0506143, -13.104, 2),
                         (-0.0506135, -13.104, 2),
                         (-0.0504665, -13.103, 2),
                         (-0.0504662, -13.103, 2),
                         (-0.0504664, -13.103, 2),
                         (-0.0504662, -13.103, 2),
                         (-0.0504662, -13.103, 2),
                         (-0.0504664, -13.103, 2),
                         (-0.0504662, -13.103, 2),
                         (-0.0504662, -13.103, 2),
                         (-0.050466, -13.103, 2),
                         (-0.0504656, -13.103, 2)], columns=['e_phase_separation', 'energy_corrected', 'nsites'])
    print(correct_composition(ScNi))


if __name__ == '__main__':
    main()
    # test_correcting()
