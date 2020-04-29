from keras.layers import Activation
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Embedding
from keras.layers import Input
from keras.layers import LSTM
from keras.models import Model

# Define RNN Architecture
def RNN(max_seq_len, vocab_size):
    inputs = Input(name='inputs', shape=[max_seq_len])
    layer = Embedding(vocab_size, 64, input_length=max_seq_len)(inputs)
    layer = LSTM(64, return_sequences = True)(layer)
    layer = Dropout(0.5)(layer)
    layer = LSTM(64)(layer)
    layer = Dense(256, name='FC1')(layer)
    layer = Dropout(0.5)(layer)
    layer = Dense(1, name='out_layer')(layer)
    layer = Activation('sigmoid')(layer)
    model = Model(inputs=inputs, outputs=layer)
    return model
