from util import remove_batch_ids, load, save
from argparse import ArgumentParser
from pathlib import Path
from tqdm import tqdm


def remove_metals(data, threshold):
    metal_ids = set()
    for i, (batch_id,) in enumerate(data["batch_ids"]):
        if data["target"]["band_gap_ind"][i, 0] < threshold:
            metal_ids.add(batch_id)
    remove_batch_ids(data, metal_ids)


def main():
    parser = ArgumentParser()
    parser.add_argument("data", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--threshold", type=float, default=0.1)
    args = parser.parse_args()

    data_path: Path = args.data
    target_dir: Path = args.target
    threshold = args.threshold

    sub_dirs = ("val", "test")
    target_val_dir = target_dir / "val"
    target_test_dir = target_dir / "test"
    target_val_dir.mkdir(parents=True, exist_ok=True)
    target_test_dir.mkdir(parents=True, exist_ok=True)

    for file in tqdm(list(data_path.glob("*.pickle.gz"))):
        data = load(file)
        remove_metals(data, threshold)
        save(data, target_dir / file.name)

    for sub_dir in sub_dirs:
        for file in tqdm(list(data_path.glob(f"{sub_dir}/*.pickle.gz"))):
            data = load(file)
            remove_metals(data, threshold)
            save(data, target_dir / sub_dir / file.name)


if __name__ == '__main__':
    main()
