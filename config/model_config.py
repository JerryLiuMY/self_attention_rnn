from tensorboard.plugins.hparams import api as hp

rnn_nums_hp = hp.HParam("rnn_nums", hp.Discrete([2]))
rnn_dims_hp = hp.HParam("rnn_dims", hp.Discrete([70, 100, 125, 150, 200]))
dnn_nums_hp = hp.HParam("dnn_nums", hp.Discrete([2]))

heads_hp = hp.HParam("heads", hp.Discrete([4, 8]))
emb_dims_hp = hp.HParam("emb_dims", hp.Discrete([32, 64, 128]))
ffn_dims_hp = hp.HParam("ffn_dims", hp.Discrete([16, 32, 64]))
