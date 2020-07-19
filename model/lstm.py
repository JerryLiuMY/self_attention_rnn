import os
import itertools
import numpy as np
import tensorflow as tf
from global_settings import DATA_FOLDER
from sklearn.metrics import confusion_matrix
from tensorflow.keras.layers import GRU, Dropout, Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import TensorBoard
from tensorboard.plugins.hparams import api as hp
from datetime import datetime
from config.train_config import train_config
from config.model_config import rnn_config
from tools.data_tools import data_loader, data_generator, load_one_hot, w
from config.model_config import rnn_nums_hp, rnn_dims_hp, dnn_nums_hp


generator, epoch = train_config['generator'], train_config['epoch']
batch, metrics = train_config['batch'], train_config['metrics']
drop = rnn_config['drop']


def run_lstm(dataset_name):
    hyp_path = os.path.join(DATA_FOLDER, f'{dataset_name}_log', 'hyper_params')
    with tf.summary.create_file_writer(hyp_path).as_default():
        hp.hparams_config(
            hparams=[rnn_nums_hp, rnn_dims_hp, dnn_nums_hp],
            metrics=[hp.Metric(metric) for metric in metrics],
        )

    rnn_nums, rnn_dims, dnn_nums = rnn_nums_hp.domain.values, rnn_dims_hp.domain.values, dnn_nums_hp.domain.values
    for rnn_num, rnn_dim, dnn_num in itertools.product(rnn_nums, rnn_dims, dnn_nums):
        hyper_params = {rnn_nums_hp: rnn_num, rnn_dims_hp: rnn_dim, dnn_nums_hp: dnn_num}
        lstm_log(dataset_name, hyper_params)


def lstm_log(dataset_name, hyper_params):
    rnn_num, rnn_dim, dnn_num = hyper_params[rnn_nums_hp], hyper_params[rnn_dims_hp], hyper_params[dnn_nums_hp]
    hyp_dir = os.path.join(DATA_FOLDER, f'{dataset_name}_log', 'hyper_params')
    if not os.path.isdir(hyp_dir): os.mkdir(hyp_dir)
    log_name = '-'.join([f'rnn_num_{rnn_num}', f'rnn_dim_{rnn_dim}', f'dnn_num_{dnn_num}'])
    log_path = os.path.join(hyp_dir, '-'.join([log_name, datetime.now().strftime('%Y%m%d-%H%M%S')]))

    print('--- Starting trial: %s' % log_name)
    print({h.name: hyper_params[h] for h in hyper_params})

    lstm_step(dataset_name, hyper_params, log_path)


def lstm_step(dataset_name, hyper_params, log_path):
    metric_callbacks = TensorBoard(log_dir=log_path)
    hypers_callbacks = hp.KerasCallback(writer=log_path, hparams=hyper_params)
    model = lstm(dataset_name, hyper_params)

    if generator:
        zip_train = data_generator(dataset_name, 'train')
        x_valid, y_valid = data_loader(dataset_name, 'valid')
        model.fit(
            x=zip_train, epochs=epoch, verbose=1,
            validation_data=(x_valid, y_valid), callbacks=[metric_callbacks, hypers_callbacks],
            max_queue_size=10, workers=5, use_multiprocessing=False
        )
    else:
        x_train, y_train = data_loader(dataset_name, 'train')
        x_valid, y_valid = data_loader(dataset_name, 'valid')
        model.fit(
            x=x_train, y=y_train, batch_size=batch, epochs=epoch, verbose=1,
            validation_data=(x_valid, y_valid), callbacks=[metric_callbacks, hypers_callbacks]
        )

    x_evalu, y_true = data_loader(dataset_name, 'valid')

    confusion_matrix(y_true.argmax(axis=1), y_pred.argmax(axis=1))


def lstm(dataset_name, hyper_params):
    model = Sequential()
    model.add(tf.keras.layers.Masking(mask_value=0.0, dtype=np.float64, input_shape=(None, w * 2)))
    model.add(GRU(units=hyper_params[rnn_dims_hp]))

    for _ in range(hyper_params[rnn_nums_hp]-1):
        model.add(GRU(units=hyper_params[rnn_dims_hp]))

    for _ in range(hyper_params[dnn_nums_hp]):
        model.add(Dense(units=hyper_params[rnn_dims_hp]*2, activation='tanh'))
        model.add(Dropout(rate=drop))

    encoder = load_one_hot(dataset_name)
    model.add(Dense(len(encoder.categories_[0]), activation='softmax'))

    model.compile(
        loss='categorical_crossentropy',
        optimizer='adam',
        metrics=metrics)

    return model


# loop 10 times
# Output to categorical & confusion matrix
# Stop training after loss stabilize
# k-fold validation
# attention model
# Phased LSTM

