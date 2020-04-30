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
    with open("config.yml", 'r') as file:
        config = yaml.safe_load(file)
except Exception as e:
    print('Error reading the config file')

# Load survey info
print('Loading Dataframe')
# df = pd.read_csv('data/survey.csv', sep="\t",
#                   header=None, names=["intent", "valid"])
df = pd.read_csv('data/mar_cumulative.csv')

# # Cast intent col to string
df['intent'] = df.intent.apply(str)

# Clean text
df['intent'] = df.intent.apply(data_proc.stripPunctuation)
df['intent'] = df.intent.apply(data_proc.stripCaps)
df['intent'] = df.intent.apply(data_proc.expandContractions)
df['intent'] = df.intent.apply(data_proc.stripStopWords)

# create X (input) and Y (expected)
X = df.intent
Y = df.valid

# create new Label encoder
label_encoder = LabelEncoder()
Y = label_encoder.fit_transform(Y)
YES_VAL = label_encoder.transform(["yes"])
NO_VAL = label_encoder.transform(["no"])
Y = Y.reshape(-1, 1)

# Train/Test split based on config
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=config['TRAIN_TEST_SPLIT'])

print('-- Some sample intents --')
print(X.tail(5))

# Data processing
# make tokenizer
tokenizer = Tokenizer(num_words=config['TOKENIZER_VOCAB_SIZE'], oov_token = "<OOV>")
tokenizer.fit_on_texts(X_train)

print("df size before augmentation: %d" % len(X_train.index))

### Data Augmentation
aug_config = config['AUG']
delta = []

# sentence variations
sentence_var_config = aug_config['SENTENCE_VAR']
print("performing sentence variation augmentation %d times" % sentence_var_config['TOTAL'])
for row in df.sample(sentence_var_config['TOTAL']).iterrows():
  intent = row[1]["intent"]
  valid = YES_VAL if row[1]["valid"] == "yes" else NO_VAL
  variations = data_proc.getVariations(intent, sentence_var_config['VARS_PER'], sentence_var_config['MUTATION_PROB'])
  delta += [[v, valid] for v in variations]

# sentence negations (only on df yes cols)
sentence_neg_config = aug_config['SENTENCE_NEG']
print("performing sentence negation augmentation %d times" % sentence_neg_config['TOTAL'])
for row in df[df.valid == "yes"].sample(sentence_neg_config['TOTAL']).iterrows():
  intent = row[1]["intent"]
  neg = data_proc.negation(intent)
  delta += [[neg, NO_VAL]]

# shuffled sentences
shuffle_config = aug_config['SHUFFLE']
print("performing sentence shuffle augmentation %d times" % shuffle_config['TOTAL'])
for row in df[df.intent.str.split().apply(len) > 3].sample(shuffle_config['TOTAL']).iterrows():
  intent = data_proc.randShuffle(row[1]["intent"])
  delta += [[intent, NO_VAL]]

# garbage sentences
garbage_config = aug_config['GARBAGE']
print("performing garbage sentence augmentation %d times" % garbage_config['TOTAL'])
for _ in range(garbage_config['TOTAL']):
  intent = data_proc.literalGarbage(garbage_config['LENGTH_LOWER_BOUND'], garbage_config['LENGTH_UPPER_BOUND'])
  delta += [[intent, NO_VAL]]

# vocab mix sentences
vocab_mix_config = aug_config['VOCAB_GARBAGE']
print("performing vocab mix sentence augmentation %d times" % vocab_mix_config['TOTAL'])
t_tokenizer = Tokenizer(num_words=config['TOKENIZER_VOCAB_SIZE'], oov_token = "<OOV>")
t_tokenizer.fit_on_texts(df.intent)
delta += [[intent, NO_VAL] for intent in data_proc.vocabGarbage(vocab_mix_config['TOTAL'], vocab_mix_config['TOPK'], t_tokenizer.word_counts)]

appendDF = pd.DataFrame(delta, columns = ['intent', 'valid'])
X_train = X_train.append(appendDF.intent)
Y_train = np.append(Y_train, appendDF.valid)
print("df size after augmentation: %d" % len(X_train.index))

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
          validation_split=config['VALIDATION_SPLIT'])

# Run model on test set
test_seqs = tokenizer.texts_to_sequences(X_test)
padded_test_seqs = sequence.pad_sequences(
    test_seqs, maxlen=config['SEQUENCE_MAX_LENGTH'])
accr = model.evaluate(padded_test_seqs, Y_test)
print('Test set\n  Loss: {:0.4f}\n  Accuracy: {:0.2f}'.format(
    accr[0], accr[1]*100))

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
model.save("models/" + model_name + "/weights.h5")
print("Saved model to disk")

# save model as JSON
model_json = model.to_json()
with open("models/" + model_name + "/model.json", "w") as file:
    file.write(model_json)

# save tokenizer as JSON
tokenizer_json = tokenizer.to_json()
with open("models/" + model_name + "/tokenizer.json", 'w', encoding='utf-8') as file:
    file.write(json.dumps(tokenizer_json, ensure_ascii=True))

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