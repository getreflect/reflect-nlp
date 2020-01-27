class Model():
    def __init__(self, model_name: str, threshold: int):
        self.MODEL_DIR = "models/" + mode_name + "/"
        self.threshold = threshold

        # load json and create model
        json_file = open(self.MODEL_DIR + 'model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.loaded_model = model_from_json(loaded_model_json)

        # load weights into new model
        self.loaded_model.load_weights(self.MODEL_DIR + "model.h5")

        # read params from details file
        print("Loaded model from disk")

    def pred(self, X: str) -> bool:
        seq = tokenizer.texts_to_sequences([X])
        padded_seq = sequence.pad_sequences(
            seq, maxlen=self.SEQUENCE_MAX_LENGTH)
        preds = model.predict(padded_seq)
        return preds > self.threshold
