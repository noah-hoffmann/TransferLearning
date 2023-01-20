import matplotlib.pyplot as plt
import pandas as pd
import os
import re
from glob import glob
import warnings


def csv_to_dataframe(epoch_path, val_path, tag='val mae'):
    val_df = pd.read_csv(val_path)[['Step', 'Value']].rename(columns={'Value': tag})
    epoch_df = pd.read_csv(epoch_path)[['Step', 'Value']].rename(columns={'Value': 'epoch'}).drop_duplicates(
        subset='Step')
    return pd.merge(val_df, epoch_df, on='Step', how='left')[['epoch', tag]]


def get_run(path, tag='val_mae'):
    files = glob(path)
    epoch_file, tag_file = None, None
    for file in files:
        if file.endswith('epoch.csv'):
            epoch_file = file
        elif file.endswith(f'{tag}.csv'):
            tag_file = file
    if epoch_file is None:
        raise ValueError(f'Could not find epoch file! For {path = }')
    if tag_file is None:
        raise ValueError(f'Could not find {tag} file!')
    return csv_to_dataframe(epoch_file, tag_file, tag=tag)


def get_training_run(database, target, root_dir='tb_logs', tag='val_mae'):
    path = os.path.join(root_dir, 'training', database, target, '*.csv')
    return get_run(path, tag)


def find_transfer_runs(root_dir='tb_logs', tag='val_mae'):
    pattern = re.compile(r'^([a-z_]+)_([a-z-]+)_to_([a-z_]+)_([a-z-]+)$')
    dirs = os.listdir(os.path.join(root_dir, 'transfer'))
    transfer_runs = []
    for dir in dirs:
        match = pattern.match(dir)
        if match is None:
            warnings.warn(f'Directory {dir!r} does not match expected pattern! Directory will be ignored!')
            continue
        target_database = match.group(3)
        target = match.group(4)
        df = get_training_run(target_database, target, root_dir=root_dir, tag=tag).rename(columns={tag: 'original'})
        sub_dirs = os.listdir(os.path.join(root_dir, 'transfer', dir))
        try:
            runs = [get_run(os.path.join(root_dir, 'transfer', dir, sub_dir, '*.csv'), tag=tag) for sub_dir in sub_dirs]
        except ValueError as e:
            warnings.warn(str(e))
            continue
        for sub_dir, run in zip(sub_dirs, runs):
            df = pd.merge(df, run.rename(columns={tag: sub_dir.replace('_', ' ')}), on='epoch', how='outer')
        transfer_runs.append((dir, df))
    return transfer_runs


def get_text(dataset, property):
    if property == "volume":
        return f"{dataset.upper()} volume"
    else:
        return rf"$\mathrm{{E}}_{{\mathrm{{{property.split('-')[1].capitalize()}}}}}^{{\mathrm{{{dataset.upper()}}}}}$"


def get_title(run: str):
    pattern = re.compile(r'^([a-z_]+)_([a-z-]+)_to_([a-z_]+)_([a-z-]+)$')
    match = pattern.match(run)
    dataset1, property1, dataset2, property2 = match.groups()
    return get_text(dataset1, property1) + " to " + get_text(dataset2, property2)


def main():
    runs = find_transfer_runs()
    save_path = os.path.join('plots', '{run}.{ext}')
    extensions = ['pdf']  # , 'png']
    units = {
        'volume': r'$\mathrm{\AA}^3$ atom$^{-1}$',
        'e-form': r'eV/atom',
        'e-hull': r'eV/atom'
    }
    plt.rcParams.update({
        "text.usetex": True
    })
    for run, df in runs:
        # if run in ("pbe_volume_to_scan_e-form", "pbe_e-form_to_scan_volume"):
        #     plt.yscale('log')
        target = run[run.rfind('_') + 1:]
        df.plot(x='epoch')
        plt.gca().tick_params(axis='both', labelsize=15)
        plt.xlabel('epoch', fontsize=17)
        plt.ylabel(f'val MAE [{units[target]}]', fontsize=17)
        plt.title(get_title(run),
                  fontsize=17)
        plt.legend(fontsize=17)
        if run == "pbe_volume_to_scan_e-form":
            plt.ylim((0.01, 0.25))
        elif run == "pbe_e-form_to_scan_volume":
            plt.ylim((0.15, 0.85))
        plt.tight_layout()
        for ext in extensions:
            plt.savefig(save_path.format(run=run, ext=ext))
        plt.show()


if __name__ == '__main__':
    main()
