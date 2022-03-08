from CGAT.lightning_module import LightningModel
from CGAT.data import CompositionData
import torch
from torch.utils.data import DataLoader
import os


def main():
    path = os.path.join('pbe', 'prepared', 'data_0_10000.pickle.gz')
    model_path = 'example.ckpt'

    model = LightningModel.load_from_checkpoint(model_path, train=False)
    dataset = CompositionData(
        data=path,
        fea_path=model.hparams.fea_path,
        max_neighbor_number=model.hparams.max_nbr,
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

    for i, batch in enumerate(dataloader):
        with torch.no_grad():
            print(i)
            model.evaluate(batch)


if __name__ == '__main__':
    main()
