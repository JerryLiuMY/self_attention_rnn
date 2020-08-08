from model.base import Base, FoldBase
from config.exec_config import train_config

use_gen = train_config['use_gen']


class PhasedLSTM(Base):

    def __init__(self, dataset_name, hyper_param, exp_dir):
        super().__init__(dataset_name, hyper_param, exp_dir)
        self._load_data('sim')


class FoldPhasedLSTM(PhasedLSTM, FoldBase):

    def __init__(self, dataset_name, hyper_param, exp_dir, fold):
        FoldBase.__init__(self, dataset_name, hyper_param, exp_dir, fold)
