import psycopg2
from getpass import getpass
import numpy as np
from glob import glob
import pickle
import gzip as gz
import re


def connect(*, dbname="agm_ht", user="noah", password=None):
    if password is None:
        password = getpass()
    conn = psycopg2.connect(dbname=dbname,
                            user=user,
                            password=password)
    return conn.cursor()


def remove_batch_ids(data: dict, batch_ids: set, inplace: bool = True, modify_batch_ids: bool = True) -> dict:
    if not modify_batch_ids:
        batch_ids = batch_ids.copy()
    # create list of indices which have to be removed
    indices_to_remove = []
    for i, (batch_id,) in enumerate(data['batch_ids']):
        if batch_id in batch_ids:
            indices_to_remove.append(i)
            batch_ids.remove(batch_id)
    # reverse list of indices to enable easy removing of items of a list by consecutive pops
    indices_to_remove.reverse()
    if inplace:
        new_data = data
    else:
        new_data = {}
    new_data['input'] = np.delete(data['input'], indices_to_remove, axis=1)
    ids: list = data['batch_ids'].copy()
    for i in indices_to_remove:
        ids.pop(i)
    new_data['batch_ids'] = ids
    new_data['batch_comp'] = np.delete(data['batch_comp'], indices_to_remove)
    if not inplace:
        new_data['target'] = {}
    for target in data['target']:
        new_data['target'][target] = np.delete(data['target'][target], indices_to_remove)
    new_data['comps'] = np.delete(data['comps'], indices_to_remove)

    return new_data


def load(file):
    return pickle.load(gz.open(file))


def get_num(file):
    pattern = re.compile(r"data_(\d+)_\d+\.pickle\.gz")
    return int(pattern.search(file).group(1))


def get_files(path):
    return sorted(glob(path), key=get_num)


def save(data, file):
    pickle.dump(data, gz.open(file, 'wb'))
