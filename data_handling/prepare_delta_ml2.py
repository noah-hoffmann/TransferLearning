from util import load, save, glob, remove_batch_ids
import os.path
from tqdm import tqdm
import warnings


def get_files(data_dir, pattern="*.pickle.gz"):
    return glob(os.path.join(data_dir, pattern)) + glob(os.path.join(data_dir, "test", pattern)) + glob(
        os.path.join(data_dir, "val", pattern))


def main():
    pbe_dir = "pbe/band_gap_prepared"
    pbe_files = get_files(pbe_dir)
    pbe_hulls = {}
    print("Reading PBE hulls")
    for file in tqdm(pbe_files):
        data = load(file)
        for i, (batch_id,) in enumerate(data["batch_ids"]):
            pbe_hulls[batch_id] = data["target"]["e_above_hull_new"][i, 0]

    scan_dir = "scan/corrected_scan/band_gap_prepared"
    target_dir = "scan/corrected_scan/delta_ml_prepared"
    scan_files = get_files(scan_dir)
    for file in tqdm(scan_files):
        data = load(file)
        data["target"]["delta_e_above_hull_new"] = data["target"]["e_above_hull_new"].copy()
        to_remove = set()
        for i, (batch_id,) in enumerate(tqdm(data["batch_ids"])):
            if batch_id not in pbe_hulls:
                warnings.warn(f"{batch_id = } does not exist in pbe files, skipping this entry!")
                to_remove.add(batch_id)
                continue
            data["target"]["delta_e_above_hull_new"][i, 0] = data["target"]["e_above_hull_new"][i, 0] - pbe_hulls[batch_id]

        remove_batch_ids(data, to_remove)
        save(data, os.path.join(target_dir, file.split('/', maxsplit=3)[-1]))


if __name__ == '__main__':
    main()
