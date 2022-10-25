import torch
from CGAT.lightning_module import LightningModel, collate_fn
from tqdm import tqdm
from CGAT.data import CompositionData
import os.path
from glob import glob
from argparse import ArgumentParser
from torch.utils.data import DataLoader
import numpy as np


def main():
    parser = ArgumentParser()

    parser.add_argument(
        '--ckp',
        type=str,
        default='',
        help='ckp path',
        required=True
    )

    parser.add_argument(
        '--data', '-d',
        type=str,
        help='directory to test files'
    )

    parser.add_argument(
        '--fea-path',
        default='embeddings/matscholar-embedding.json'
    )

    parser.add_argument(
        '--batch-size', '-b',
        type=int,
        default=500
    )

    hparams = parser.parse_args()
    hparams.train = False

    model = LightningModel.load_from_checkpoint(hparams.ckp, train=False)
    model.cuda()
    files = sorted(glob(os.path.join(hparams.data, '*.pickle.gz')))

    targets = []
    predictions = []

    for file in tqdm(files):
        dataset = CompositionData(
            data=file,
            fea_path=hparams.fea_path,
            max_neighbor_number=model.hparams.max_nbr,
            target=model.hparams.target
        )
        loader = DataLoader(dataset, batch_size=hparams.batch_size, shuffle=False, collate_fn=collate_fn)
        with torch.no_grad():
            for batch in loader:
                _, _, prediction, target, _ = model.evaluate(batch)
                targets.append(target.cpu().numpy())
                predictions.append(prediction.cpu().numpy())
    print(
        f"Mean Absoulte Error = {np.abs(np.concatenate(targets, axis=None) - np.concatenate(predictions, axis=None)).mean()}")


if __name__ == '__main__':
    main()
