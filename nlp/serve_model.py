import json
import sys
import getopt
import yaml

import data_proc
import train
import pandas as pd

from tqdm import tqdm

from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.models import model_from_json  # fix threads crash

class Model():

    def __init__(self, model_name: str, threshold: int):
        self.MODEL_DIR = "models/" + model_name + "/"
        self.threshold = threshold
        self.loadModel()
        self.loadTokenizer()
        self.loadWeights()
        self.params = self.loadParams()

        # read params from details file
        print("Loaded model from disk")

    def loadTokenizer(self):
        with open(self.MODEL_DIR + 'tokenizer.json', 'r') as f:
            data = json.load(f)
            self.tokenizer = tokenizer_from_json(data)

    def loadModel(self):
        # load json and create model
        json_file = open(self.MODEL_DIR + 'model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.loaded_model = model_from_json(loaded_model_json)

    def loadWeights(self):
        # load weights into new model
        self.loaded_model.load_weights(self.MODEL_DIR + "weights.h5")

    def loadParams(self):
        # load saved parameters
        with open(self.MODEL_DIR + 'details.yml', 'r') as config:
            return yaml.full_load(config)

    def pred(self, X: str):
        # clean input X
        X = data_proc.stripPunctuation(X)
        X = data_proc.stripCaps(X)
        X = data_proc.expandContractions(X)
        X = data_proc.stripStopWords(X)

        # tokenize input
        seq = self.tokenizer.texts_to_sequences([X])

        # pad seqs
        padded_seq = sequence.pad_sequences(
            seq, maxlen=self.params["SEQUENCE_MAX_LENGTH"])

        # predict
        preds = self.loaded_model.predict(padded_seq)[0][0]

        # return thresholded value
        return (preds > self.threshold)

    def eval_on_csv(self, path):
        df = pd.read_csv(path)
        train.clean_df(df)
        X = df.intent
        Y = df.valid

        print('Evalutating on given data...')
        out = list(zip(df.valid, [self.pred(S) for S in tqdm(df.intent)]))

        incorrect = []
        for (i, (label, pred)) in enumerate(out):
            label_val = label == "yes"
            if label_val != pred:
                incorrect.append(f"'{X[i]}' -> {pred} != {label_val}")

        print('Examples model got wrong:')
        print("\n".join(incorrect))
        return (1 - (len(incorrect) / len(out))) * 100

# parse command line arguments if run directly
if __name__ == '__main__':
    # read command line flags
    argv = sys.argv[1:]

    # define default parameters
    model = 'acc85.95'
    threshold = 0.5
    intent = 'need to do some work'

    # acceptable flags -> -h, -i, -h, -t, -e
    # full length flags -> --help, --intent, --model, --threshold, --eval
    unixOptions = "hm:t:i:e:"
    gnuOptions = ["help", "intent=", "model", "threshold", "eval"]

    # string to print on -h or err
    errString = 'serve_model.py -m <nameofmodel> -t <threshold> -i <intent>'

    try:
        opts, args = getopt.getopt(argv, unixOptions, gnuOptions)
    except getopt.GetoptError:
        # error when parsing flags
        print(errString)
        sys.exit(2)
    for opt, arg in opts:
        print(opt, arg)
        if opt in ("-h", "--help"):
            print(errString)
            sys.exit(2)
        elif opt in ("-t", "--threshold"):
            threshold = float(arg)
        elif opt in ("-i", "--intent"):
            intent = arg
        elif opt in ("-m", "--model"):
            model = arg
        elif opt in ("-e", "--eval"):
            m = Model(model, threshold)
            print(f"Accuracy: {m.eval_on_csv(arg)}")
            sys.exit(0)

    # create actual model
    m = Model(model, threshold)
    print('Predicting using model %s with threshold %.2f on intent "%s"' %
          (model, threshold, intent))
    print('Output -> %s' % m.pred(intent))
