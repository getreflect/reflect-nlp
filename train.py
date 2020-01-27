# -- Data Processing Imports --
import matplotlib.pyplot as plt  # graphing
import numpy as np  # more data processing stuff
import pandas as pd  # data processing/analysis
import os

# -- Deep Learning Libraries --
from keras.callbacks import EarlyStopping
from keras.optimizers import RMSprop
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# -- Local imports --
import net
import data_proc

# -- Params --
TOKENIZER_VOCAB_SIZE = 500
SEQUENCE_MAX_LENGTH = 75
BATCH_SIZE = 128
NUM_EPOCHS = 10
TRAIN_TEST_SPLIT = 0.1
VALIDATION_SPLIT = 0.1
TAIL_SIZE = 10

# Load survey info
print('Loading Dataframe')
df = pd.read_csv('data/survey.csv', sep="\t",
                 header=None, names=["intent", "valid"])

# Clean text
numPunc = df.intent.apply(data_proc.countPunctuation)
df['intent'] = df.intent.apply(data_proc.stripPunctuation)

numCaps = df.intent.apply(data_proc.countCaps)
df['intent'] = df.intent.apply(data_proc.stripCaps)
df['intent'] = df.intent.apply(data_proc.rmPersonalPrefix)
print('-- Some sample intents --')
print(df.intent.tail(5))

# create X (input) and Y (expected)
X = df.intent
Y = df.valid

# create new Label encoder
labelEncoder = LabelEncoder()
Y = labelEncoder.fit_transform(Y)
Y = Y.reshape(-1, 1)
# output is now one hot encoded

# Train/Test split, 15% test set
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=TRAIN_TEST_SPLIT)

# Data processing
tokenizer = Tokenizer(num_words=TOKENIZER_VOCAB_SIZE)
tokenizer.fit_on_texts(X_train)
seqs = tokenizer.texts_to_sequences(X_train)
padded_seqs = sequence.pad_sequences(
    seqs, maxlen=SEQUENCE_MAX_LENGTH)

# Load Network Architecture
model = net.RNN(SEQUENCE_MAX_LENGTH, TOKENIZER_VOCAB_SIZE)
model.summary()
model.compile(loss='binary_crossentropy',
              optimizer=RMSprop(), metrics=['accuracy'])

# Model Training
model.fit(padded_seqs, Y_train, batch_size=BATCH_SIZE, epochs=NUM_EPOCHS,
          validation_split=VALIDATION_SPLIT, callbacks=[EarlyStopping(monitor='val_loss', min_delta=0.000001, patience = 3)])


test_seqs = tokenizer.texts_to_sequences(X_test)
padded_test_seqs = sequence.pad_sequences(
    test_seqs, maxlen=SEQUENCE_MAX_LENGTH)
accr = model.evaluate(padded_test_seqs, Y_test)
print('Test set\n  Loss: {:0.3f}\n  Accuracy: {:0.3f}'.format(
    accr[0], accr[1]))

seq = tokenizer.texts_to_sequences(df.intent.tail(TAIL_SIZE))
padded_seq = sequence.pad_sequences(seq, maxlen=SEQUENCE_MAX_LENGTH)
preds = model.predict(padded_seq)

out = list(zip(df.intent.tail(TAIL_SIZE), df.valid.tail(TAIL_SIZE), preds))
for obs in out:
    print('Intent: %s   Actual Class: %s   Predicted Class: %s' %
          (obs[0], obs[1], "yes" if obs[2][0] > 0.5 else "no"))


# Define Model Name
model_name = "acc%d" % (accr[1] * 100)
os.mkdir('models/' + model_name)

# save weights as HDF5
model.save_weights("models/" + model_name + "/weights.h5")
print("Saved model to disk")

# save model as JSON
model_json = model.to_json()
with open("models/" + model_name + "/model.json", "w") as json_file:
    json_file.write(model_json)

# write training details to file
f = open("models/" + model_name + "/details.txt", "w")
f.write("Tokenizer Vocab Size: " + str(TOKENIZER_VOCAB_SIZE) + "\n")
f.write("Max Token Sequence Length: " + str(SEQUENCE_MAX_LENGTH) + "\n")
f.write("Batch size: " + str(BATCH_SIZE) + "\n")
f.write("Number of Epochs: " + str(NUM_EPOCHS) + "\n")
f.write("Train/Test Split Ratio: " + str(TRAIN_TEST_SPLIT) + "\n")
f.write("Validation Split Ratio: " + str(VALIDATION_SPLIT))
f.close()