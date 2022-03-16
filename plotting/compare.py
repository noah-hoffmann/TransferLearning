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
        raise ValueError('Could not find epoch file!')
    if tag_file is None:
        raise ValueError(f'Could not find {tag} file!')
    return csv_to_dataframe(epoch_file, tag_file, tag=tag)


def get_training_run(database, target, root_dir='tb_logs', tag='val_mae'):
    path = os.path.join(root_dir, 'training', database, target, '*.csv')
    return get_run(path, tag)


def find_transfer_runs(root_dir='tb_logs', tag='val_mae'):
    pattern = re.compile(r'^([a-z]+)_([a-z-_]+)_to_([a-z]+)_([a-z-_]+)$')
    dirs = os.listdir(os.path.join(root_dir, 'transfer'))
    transfer_runs = []
    for dir in dirs:
        match = pattern.match(dir)
        if match is None:
            warnings.warn(f'Directory {dir} does not match expected pattern! Directory will be ignored!')
            continue
        target_database = match.group(3)
        target = match.group(4)
        df = get_training_run(target_database, target, root_dir=root_dir, tag=tag).rename(columns={tag: 'original'})
        sub_dirs = os.listdir(os.path.join(root_dir, 'transfer', dir))
        runs = [get_run(os.path.join(root_dir, 'transfer', dir, sub_dir, '*.csv'), tag=tag) for sub_dir in sub_dirs]
        for sub_dir, run in zip(sub_dirs, runs):
            df = pd.merge(df, run.rename(columns={tag: sub_dir}), on='epoch', how='outer')
        transfer_runs.append((dir, df))
    return transfer_runs


def main():
    runs = find_transfer_runs()
    save_path = os.path.join('plots', '{run}.{ext}')
    extensions = ['pdf', 'png']
    for run, df in runs:
        df.plot(x='epoch')
        plt.ylabel('val mae')
        plt.title(run.replace('_', ' '))
        for ext in extensions:
            plt.savefig(save_path.format(run=run, ext=ext))
        plt.show()


if __name__ == '__main__':
    main()
