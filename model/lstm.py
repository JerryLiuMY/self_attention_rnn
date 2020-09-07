import numpy as np
from model._base import _Base, _FoldBase
from tensorflow.keras.layers import LSTM, Dense, ReLU, Masking
from tensorflow.keras.layers import LayerNormalization, GlobalAveragePooling1D, TimeDistributed
from tensorflow.keras.models import Sequential
from tensorflow.keras import regularizers
from config.data_config import data_config
from config.model_config import rnn_nums_hp, rnn_dims_hp, dnn_nums_hp
from config.exec_config import train_config, strategy

use_gen, epoch = train_config['use_gen'], train_config['epoch']
ws = data_config['ws']


class SimpleLSTM(_Base):

    def __init__(self, dataset_name, hyper_param, exp_dir):
        super().__init__(dataset_name, hyper_param, exp_dir)
        with strategy.scope():
            self._build()
            self._compile()

    def _build(self):
        # WARNING: Masking is only supported in the CPU environment (not supported for CuDNN RNNs)
        model = Sequential()
        model.add(Masking(mask_value=np.float32(3.14159), input_shape=(None, ws[self.dataset_name][0] * 2)))

        for _ in range(self.hyper_param[rnn_nums_hp]):
            # foo = True if _ < self.hyper_param[rnn_nums_hp] - 1 else False
            model.add(LSTM(
                units=self.hyper_param[rnn_dims_hp], return_sequences=True,
                recurrent_regularizer=regularizers.l2(0.1))
            )
            model.add(LayerNormalization())

        for _ in range(self.hyper_param[dnn_nums_hp]):
            model.add(TimeDistributed(Dense(
                units=self.hyper_param[rnn_dims_hp] * 2,
                kernel_regularizer=regularizers.l2(0.1)))
            )
            model.add(LayerNormalization())
            model.add(ReLU())

        model.add(TimeDistributed(Dense(units=len(self.categories), activation='softmax'), name='softmax'))
        model.add(GlobalAveragePooling1D(data_format='channels_last'))

        self.model = model

    def _compile(self):
        self.model.compile(
            loss='categorical_crossentropy',
            optimizer='adam',
            metrics=self.metrics)

    def run(self):
        self.model.fit(
            x=self.dataset_train, validation_data=self.dataset_valid, epochs=epoch,
            verbose=1, max_queue_size=10, workers=5, callbacks=self.callbacks
        )



class FoldSimpleLSTM(SimpleLSTM, _FoldBase):

    def __init__(self, dataset_name, hyper_param, exp_dir, fold):
        _FoldBase.__init__(self, dataset_name, hyper_param, exp_dir, fold)
