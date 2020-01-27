import json
import yaml

from keras.models import model_from_json
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.text import tokenizer_from_json


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
        with open(self.MODEL_DIR + 'details.yaml', 'r') as config:
            return yaml.full_load(config)

    def pred(self, X: str) -> bool:
        # tokenize input
        seq = self.tokenizer.texts_to_sequences([X])

        # pad seqs
        padded_seq = sequence.pad_sequences(
            seq, maxlen=self.params["SEQUENCE_MAX_LENGTH"])

        # predict
        preds = self.loaded_model.predict(padded_seq)[0][0]

        # return thresholded value
        return (preds > self.threshold)

if __name__ == '__main__':
    m = Model("acc81.08", threshold=0.5)
    print(m.pred("do some work"))
