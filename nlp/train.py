# -- Data Processing Imports --
import matplotlib.pyplot as plt  # graphing
import numpy as np  # more data processing stuff
import pandas as pd  # data processing/analysis
import os
import yaml
import json
import datetime

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

# -- Parse config.yaml Parameters --
try: 
    with open ("config.yaml", 'r') as file:
        config = yaml.safe_load(file)
except Exception as e:
    print('Error reading the config file')

# Load survey info
print('Loading Dataframe')
df = pd.read_csv('data/survey.csv', sep="\t",
                 header=None, names=["intent", "valid"])

# Clean text
df['intent'] = df.intent.apply(data_proc.stripPunctuation)
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
    X, Y, test_size=config['TRAIN_TEST_SPLIT'])

# Data processing
tokenizer = Tokenizer(num_words=config['TOKENIZER_VOCAB_SIZE'])
tokenizer.fit_on_texts(X_train)
seqs = tokenizer.texts_to_sequences(X_train)
padded_seqs = sequence.pad_sequences(
    seqs, maxlen=config['SEQUENCE_MAX_LENGTH'])

# Load Network Architecture
model = net.RNN(config['SEQUENCE_MAX_LENGTH'], config['TOKENIZER_VOCAB_SIZE'])
model.summary()
model.compile(loss='binary_crossentropy',
              optimizer=RMSprop(), metrics=['accuracy'])

# Model Training
model.fit(padded_seqs, Y_train, batch_size=config['BATCH_SIZE'], epochs=config['NUM_EPOCHS'],
          validation_split=config['VALIDATION_SPLIT'], callbacks=[EarlyStopping(monitor='val_loss', min_delta=0.000001, patience=3)])

# Run model on test set
test_seqs = tokenizer.texts_to_sequences(X_test)
padded_test_seqs = sequence.pad_sequences(
    test_seqs, maxlen=config['SEQUENCE_MAX_LENGTH'])
accr = model.evaluate(padded_test_seqs, Y_test)
print('Test set\n  Loss: {:0.3f}\n  Accuracy: {:0.3f}'.format(
    accr[0], accr[1]))

# Print some example classifications from intent list
seq = tokenizer.texts_to_sequences(df.intent.tail(config['TAIL_SIZE']))
padded_seq = sequence.pad_sequences(seq, maxlen=config['SEQUENCE_MAX_LENGTH'])
preds = model.predict(padded_seq)
out = list(zip(df.intent.tail(config['TAIL_SIZE']), df.valid.tail(config['TAIL_SIZE']), preds))
for obs in out:
    print('Intent: %s   Actual Class: %s   Predicted Class: %s' %
          (obs[0], obs[1], "yes" if obs[2][0] > 0.5 else "no"))

# Define Model Name
model_name = "acc%.2f" % (accr[1] * 100)
os.mkdir('models/' + model_name)

# save weights as HDF5
model.save_weights("models/" + model_name + "/weights.h5")
print("Saved model to disk")

# save model as JSON
model_json = model.to_json()
with open("models/" + model_name + "/model.json", "w") as file:
    file.write(model_json)

# save tokenizer as JSON
tokenizer_json = tokenizer.to_json()
with open("models/" + model_name + "/tokenizer.json", 'w', encoding='utf-8') as file:
    file.write(json.dumps(tokenizer_json, ensure_ascii=False))

# write training details to YAML
detail_dict = {'TOKENIZER_VOCAB_SIZE': config['TOKENIZER_VOCAB_SIZE'],
               'SEQUENCE_MAX_LENGTH': config['SEQUENCE_MAX_LENGTH'],
               'BATCH_SIZE': config['BATCH_SIZE'],
               'NUM_EPOCHS': config['NUM_EPOCHS'],
               'TRAIN_TEST_SPLIT': config['TRAIN_TEST_SPLIT'],
               'VALIDATION_SPLIT': config['VALIDATION_SPLIT'],
               'TRAINED_AT': datetime.datetime.now()}

with open("models/" + model_name + "/details.yml", "w") as file:
    documents = yaml.dump(detail_dict, file)