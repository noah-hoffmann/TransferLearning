from CGAT.lightning_module import LightningModel
from CGAT.data import CompositionData
import torch
from torch.utils.data import DataLoader
import os
from glob import glob
from tqdm import tqdm
from argparse import ArgumentParser
from CGAT.train import run


def main():
    parser = ArgumentParser(add_help=False)
    parser = LightningModel.add_model_specific_args(parser)

    hparams = parser.parse_args()
    model = LightningModel.load_from_checkpoint('example.ckpt', **vars(hparams))

    dataset = CompositionData(
        data='prepared/data_0_10000.pickle.gz',
        fea_path=hparams.fea_path,
        max_neighbor_number=hparams.max_nbr,
        target='e-form'
    )

    params = {
        "batch_size": 1,
        "pin_memory": False,
        "shuffle": False,
        "drop_last": False
    }

    def collate_fn(datalist):
        return datalist

    model = model.cuda()
    dataloader = DataLoader(dataset, collate_fn=collate_fn, **params)

    for batch in dataloader:
        with torch.no_grad():
            print(model.evaluate(batch)[2])
        break


if __name__ == '__main__':
    run()
    # main()
