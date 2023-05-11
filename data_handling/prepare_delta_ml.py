from argparse import ArgumentParser
from util import load, save, glob, connect
import os.path
from tqdm import tqdm
from correct_e_phase_separation import find_all_affected_compositions, get_compositions
import warnings

targets = ["e_above_hull_new", "e-form", "band_gap_ind"]
query = f"SELECT formula, e_phase_separation, e_form, band_gap_ind FROM energy_runs_pbe WHERE mat_id = '{{batch_id}}';"


def add_deltas(data, cursor, affected_formulas, file, relation):
    # add new delta properties
    for p in targets:
        data["target"][f"delta_{p}"] = data["target"]["e-form"].copy()

    for i, (batch_id,) in enumerate(data["batch_ids"]):
        # execute query and get reference values
        cursor.execute(query.format(batch_id=batch_id))
        results = cursor.fetchall()
        if len(results) == 0:
            warnings.warn(f"{batch_id = } does not exist in database, skipping this entry!")
            continue
        elif len(results) > 1:
            warnings.warn(f"{batch_id = } not unique, only using first result!")
        formula, e_phase, e_form, band_gap_ind = results[0]
        # correct possibly wrong phase separation values in the database
        if formula in affected_formulas:
            try:
                e_phase = get_compositions(formula, cursor, relation).at[batch_id, 'e_phase_separation']
            except KeyError:
                warnings.warn(
                    f"Caught KeyError for {batch_id=} and {formula=} in file {file!r}!")
        # now calculate the actual delta
        data["target"]["delta_e_above_hull_new"][i, 0] = data["target"]["e_above_hull_new"][i, 0] - e_phase
        data["target"]["delta_e-form"][i, 0] = data["target"]["e-form"][i, 0] - e_form
        data["target"]["delta_band_gap_ind"][i, 0] = data["target"]["banb_gap_ind"][i, 0] - band_gap_ind


def main():
    parser = ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("target")
    # parser.add_argument("--origin", default="energy_runs_pbe")
    # parser.add_argument("-r", default="energy_runs_scan")
    args = parser.parse_args()

    target_dir = args.target

    # connect to database
    cursor = connect()

    # find all compositions, which have wrong e_phase_separation values
    print("Finding compositions, which have wrong phase separation values...")
    affected_formulas = find_all_affected_compositions(cursor, "energy_runs_pbe")

    training_files = glob(os.path.join(args.data, "*.pickle.gz"))

    sub_dirs = ("val", "test")
    target_val_dir = target_dir / "val"
    target_test_dir = target_dir / "test"
    target_val_dir.mkdir(parents=True, exist_ok=True)
    target_test_dir.mkdir(parents=True, exist_ok=True)

    for file in tqdm(training_files):
        data = load(file)

        add_deltas(data, cursor, affected_formulas, file, "energy_runs_pbe")

        save(data, os.path.join(target_dir, os.path.basename(file)))

    for sub_dir in sub_dirs:
        for file in tqdm(glob(os.path.join(target_dir, sub_dir, "*.pickle.gz"))):
            data = load(file)

            add_deltas(data, cursor, affected_formulas, file, "energy_runs_pbe")

            save(data, os.path.join(target_dir, sub_dir, os.path.basename(file)))


if __name__ == '__main__':
    main()
