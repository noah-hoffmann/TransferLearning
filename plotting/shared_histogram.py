from histograms import load_parallel
import matplotlib.pyplot as plt
import os.path
from glob import glob


def main():
    scan_path = os.path.join('scan', 'data')
    pbesol_path = os.path.join('pbesol', 'data')

    property = 'e_above_hull_new'

    print("Loading SCAN data...", flush=True)
    scan_data = load_parallel(load_parallel(glob(os.path.join(scan_path, '*.pickle.gz'))))

    print("Loading PBEsol data...", flush=True)
    pbesol_data = load_parallel(load_parallel(glob(os.path.join(pbesol_path, '*.pickle.gz'))))

    bins = 100
    plt.hist([scan_data[property], pbesol_data[property]], bins=bins)
    plt.yscale('log')

    plt.tight_layout()

    save_path = os.path.join('histograms', 'shared')
    os.makedirs(save_path, exist_ok=True)

    plt.savefig(os.path.join(save_path, f'{property}.pdf'))


if __name__ == '__main__':
    main()
