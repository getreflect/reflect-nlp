# -- Data Processing Imports --
import matplotlib.pyplot as plt  # graphing
import numpy as np  # more data processing stuff
import pandas as pd  # data processing/analysis

# -- Deep Learning Libraries --
from keras.callbacks import EarlyStopping
from keras.optimizers import RMSprop
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# -- Network Architecture
import net

# -- Params --
TOKENIZER_VOCAB_SIZE = 1000
SEQUENCE_MAX_LENGTH = 150

# Load survey info
print('Loading Dataframe')
df = pd.read_csv('data/survey.csv', sep="\t",
                 header=None, names=["intent", "valid"])
print('Number of invalid intents: %d' % len(df[df.valid == 'no']))
print('Number of valid intents: %d' % len(df[df.valid == 'yes']))

# create X (input) and Y (expected)
X = df.intent
Y = df.valid

# create new Label encoder
labelEncoder = LabelEncoder()
Y = labelEncoder.fit_transform(Y)
Y = Y.reshape(-1, 1)
# output is now one hot encoded

# Train/Test split, 15% test set
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.15)


# Data processing
tokenizer = Tokenizer(num_words=TOKENIZER_VOCAB_SIZE)
tokenizer.fit_on_texts(X_train)
seqs = tokenizer.texts_to_sequences(X_train)
padded_seqs = sequence.pad_sequences(
    seqs, maxlen=SEQUENCE_MAX_LENGTH, padding='post')

# remove I, I'm, i, im, i'm from start
# count punctuation (ellipses is one)
# remove punctuation (replace / with space)

# count caps
# remove caps

# length < 3 -> ask to describe

# Load Network Architecture
model = net.RNN(SEQUENCE_MAX_LENGTH, TOKENIZER_VOCAB_SIZE)
model.summary()
