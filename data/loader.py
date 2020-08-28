import os
import math
import numpy as np
import sklearn
import pandas as pd
import pickle
import tensorflow as tf
from global_settings import DATA_FOLDER
from sklearn.utils import class_weight
from config.exec_config import train_config
from tensorflow.keras.utils import Sequence
from datetime import datetime
from tools.data_tools import load_catalog, load_fold
from tools.data_tools import load_xy
from tools.misc import one_hot_msg, data_msg

batch = train_config['batch']


class BaseGenerator(Sequence):
    def __init__(self, dataset_name, model_name):
        self.dataset_name = dataset_name
        self.model_name = model_name
        self.catalog = pd.DataFrame()
        self.encoder = one_hot_loader(self.dataset_name, self.model_name)
        self.on_epoch_end()

    def __len__(self):
        return math.ceil(np.shape(self.catalog)[0] / batch)

    def __getitem__(self, index):
        catalog_ = self.catalog.iloc[index * batch: (index + 1) * batch, :]
        x, y, sample_weight = self._data_generation(catalog_)

        return x, y, sample_weight

    def on_epoch_end(self):
        self.catalog = sklearn.utils.shuffle(self.catalog, random_state=0)

    def _data_generation(self, catalog_):
        x, y_spar = load_xy(self.dataset_name, 'train', catalog_)
        y = self.encoder.transform(y_spar).toarray()
        sample_weight = class_weight.compute_sample_weight('balanced', y)
        x, y = x.astype(np.float32), y.astype(np.float32)

        return x, y, sample_weight


class DataGenerator(BaseGenerator):
    def __init__(self, dataset_name, model_name):
        super().__init__(dataset_name, model_name)
        self.catalog = load_catalog(self.dataset_name, 'train')


class FoldGenerator(BaseGenerator):
    def __init__(self, dataset_name, model_name, fold):
        super().__init__(dataset_name, model_name)
        self.fold = fold
        self.catalog = load_fold(self.dataset_name, 'train', self.fold)


@one_hot_msg
def one_hot_loader(dataset_name, model_name):
    dataset_folder = '_'.join([dataset_name, model_name])
    with open(os.path.join(DATA_FOLDER, dataset_folder, 'encoder.pkl'), 'rb') as handle:
        encoder = pickle.load(handle)

    return encoder


@data_msg
def data_loader(dataset_name, model_name, set_type):
    dataset_folder = '_'.join([dataset_name, model_name])
    with open(os.path.join(DATA_FOLDER, dataset_folder, set_type + '.pkl'), 'rb') as handle:
        x, y = pickle.load(handle)

    if set_type == 'train':
        sample_weight = class_weight.compute_sample_weight('balanced', y)
        dataset = tf.data.Dataset.from_tensor_slices((x, y, sample_weight))
        dataset = dataset.shuffle(np.shape(x)[0], reshuffle_each_iteration=True).batch(batch)
    else:
        dataset = tf.data.Dataset.from_tensor_slices((x, y))
        dataset = dataset.batch(batch)

    return dataset


def fold_loader(dataset_name, model_name, set_type, fold):
    print(f'{datetime.now()} Loading {dataset_name} {set_type} set fold {fold}')

    catalog = load_fold(dataset_name, set_type, fold)
    encoder = one_hot_loader(dataset_name, model_name)
    x, y_spar = load_xy(dataset_name, set_type, catalog)
    y = encoder.transform(y_spar).toarray().astype(np.float32)
    x, y = x.astype(np.float32), y.astype(np.float32)

    return x, y
