import pickle
import gzip as gz

import numpy as np
from tqdm import tqdm
from pymatgen.entries.computed_entries import ComputedStructureEntry
import os
from glob import glob
import matplotlib.pyplot as plt
from multiprocessing import Pool
import sys


def load(file):
    with gz.open(file) as f:
        data = pickle.load(f)
    return data


def get_properties(data: list[ComputedStructureEntry], property_keys):
    properties = {key: [] for key in property_keys}
    for entry in data:
        for key in property_keys:
            properties[key].append(entry.data[key])
    return properties


def load_properties(file, property_keys=('e_above_hull_new', 'e-form', 'volume')):
    return get_properties(load(file), property_keys)


def main():
    paths = [os.path.join(data_set, 'data') for data_set in [sys.argv[1]]]

    for path in paths:
        files = sorted(glob(os.path.join(path, '*.pickle.gz')))
        properties = {'e_above_hull_new': [], 'e-form': [], 'volume': []}

        # load files in parallel to speed up the loading
        with Pool() as pool:
            for data in tqdm(pool.imap_unordered(load_properties, files), total=len(files)):
                for key, item in data.items():
                    properties[key] = np.concatenate((properties[key], item))

        # for file in tqdm(files[:10]):
        #     data = get_properties(load(file), properties.keys())
        #     for key, item in data.items():
        #         properties[key].extend(item)

        save_path = os.path.join('histograms', os.path.basename(os.path.split(path)[0]))
        os.makedirs(save_path, exist_ok=True)

        items = (('e_above_hull_new', 'distance to the convex hull', 'eV atom$^{-1}$', 'hull'),
                 ('e-form', 'formation energy', 'eV atom$^{-1}$', 'formation'),
                 ('volume', 'volume', r'$\AA^3$ atom$^{-1}$', 'volume'))

        for property, label, unit, short in items:
            plt.figure()
            # remove outlier
            if sys.argv[1] == 'pbe' and property != 'volume':
                properties[property] = np.sort(properties[property])[1:]
            n, _, _ = plt.hist(properties[property], bins=15)
            bins = len(n)
            plt.xlabel(f'{label} [{unit}]', fontsize=17)
            plt.ylabel('count', fontsize=17)
            plt.yscale('log')
            plt.gca().tick_params(axis='both', labelsize=15)

            ax = plt.gca().twinx()
            bins, edges = np.histogram(properties[property], bins=bins,
                                       weights=np.full_like(properties[property], 1 / len(properties[property])))
            bins = np.cumsum(bins)
            ax.step(edges[:-1], bins, color='r')
            ax.set_ylabel('relative cumulative count', fontsize=17)

            plt.tight_layout()
            plt.savefig(os.path.join(save_path, f'{short}_histogram.pdf'))

        # plt.figure()
        # # remove outlier
        # if sys.argv[1] == 'pbe':
        #     properties['e-form'] = sorted(properties['e-form'])[1:]
        # plt.hist(properties['e-form'], bins=15)
        # plt.xlabel('formation energy [eV atom$^{-1}$]', fontsize=17)
        # plt.ylabel('count', fontsize=17)
        # plt.yscale('log')
        # plt.gca().tick_params(axis='both', labelsize=15)
        # plt.tight_layout()
        # plt.savefig(os.path.join(save_path, 'formation_histogram.pdf'))
        #
        # plt.figure()
        # plt.hist(properties['volume'], bins=15)
        # plt.xlabel(r'volume [$\AA^3$ atom$^{-1}$]', fontsize=17)
        # plt.ylabel('count', fontsize=17)
        # plt.yscale('log')
        # plt.gca().tick_params(axis='both', labelsize=15)
        # plt.tight_layout()
        # plt.savefig(os.path.join(save_path, 'volume_histogram.pdf'))

    # plt.show()


if __name__ == '__main__':
    main()
