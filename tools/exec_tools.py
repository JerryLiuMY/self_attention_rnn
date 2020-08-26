import os
import numpy as np
from global_settings import LOG_FOLDER


# create new directories
def get_log_dir(dataset_name, model_name):
    log_dir = os.path.join(LOG_FOLDER, f'{dataset_name}_{model_name}')
    os.makedirs(log_dir, exist_ok=True)

    return log_dir


def get_exp_dir(log_dir):
    past_dirs = next(os.walk(log_dir))[1]
    new_num = 0 if len(past_dirs) == 0 else np.max([int(past_dir.split('_')[-1]) for past_dir in past_dirs]) + 1
    exp_dir = os.path.join(log_dir, '_'.join(['experiment', str(new_num)]))
    os.mkdir(exp_dir)

    return exp_dir


def create_dirs(*args):
    for path in args:
        if not os.path.isdir(path):
            os.mkdir(path)


create_paths = create_dirs


# global check
def check_dataset_name(dataset_name):
    assert dataset_name.split('_')[0] in ['ASAS', 'MACHO', 'WISE', 'GAIA', 'OGLE', 'Synthesis'], 'Invalid dataset name'


def check_model_name(model_name):
    assert model_name in ['sim', 'pha', 'att'], 'Invalid model name'


def check_set_type(set_type, is_fold=False):
    if not is_fold:
        assert set_type in ['train', 'valid', 'evalu'], 'Invalid set type'
    else:
        assert set_type in ['train', 'evalu'], 'Invalid set type'