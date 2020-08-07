import os
import itertools
from global_settings import LOG_FOLDER, DATASET_NAME
from tools.utils import new_dir
from model.base import log_params
from config.model_config import rnn_nums_hp, rnn_dims_hp, dnn_nums_hp
from model.lstm import SimpleLSTM, FoldLSTM
from config.exec_config import evalu_config

kfold = evalu_config['kfold']


def run(dataset_name):
    log_dir = os.path.join(LOG_FOLDER, f'{dataset_name}_log'); os.makedirs(log_dir, exist_ok=True)
    exp_dir = new_dir(log_dir); log_params(exp_dir)
    rnn_nums, rnn_dims, dnn_nums = rnn_nums_hp.domain.values, rnn_dims_hp.domain.values, dnn_nums_hp.domain.values
    for rnn_num, rnn_dim, dnn_num in itertools.product(rnn_nums, rnn_dims, dnn_nums):
        hyper_param = {rnn_nums_hp: rnn_num, rnn_dims_hp: rnn_dim, dnn_nums_hp: dnn_num}
        exp = SimpleLSTM(dataset_name=dataset_name, hyper_param=hyper_param, exp_dir=exp_dir)
        exp.build()
        exp.run()


def run_fold(dataset_name, hyper_param):
    for fold in map(str, range(0, 10)):
        exp_dir = os.path.join(LOG_FOLDER, f'{dataset_name}_fold', f'fold_{fold}'); os.makedirs(exp_dir, exist_ok=False)
        fold_exp = FoldLSTM(dataset_name=dataset_name, hyper_param=hyper_param, exp_dir=exp_dir, fold=fold)
        fold_exp.build()
        fold_exp.run()


if __name__ == '__main__':
    run(DATASET_NAME)
