# reflect-nlp

[![CircleCI](https://circleci.com/gh/jackyzha0/reflect-nlp.svg?style=svg)](https://circleci.com/gh/jackyzha0/reflect-nlp)

the backend to determine intent validity and stats aggregation. <br>

[the main repo.](https://github.com/jackyzha0/reflect-chrome)

### Docker build instructions
1. Build latest docker image: `docker build -t jzhao2k19/reflect-nlp:latest .`
2. Run the image on port 8081: `docker run -p 5000:5000 jzhao2k19/reflect-nlp:latest`

### Running the NLP Model
This project depends on a bunch of Python libraries. Install them by doing `pip install sklearn keras pandas numpy matplotlib`

<br>

For local development, you can run the server by doing `python server.py`, which will start a local server on port 5000. 

### Training the NLP Model

You can train a new version of the neural network on the `data/survey.csv` data by doing `python train.py`. This will begin training of a basic 64 cell LSTM model (which is defined in `net.py`). You can configure the training parameters which are constants at the top of `train.py`.

```python
TOKENIZER_VOCAB_SIZE = 500 # Vocabulary size of the tokenizer
SEQUENCE_MAX_LENGTH = 75 # Maximum sequence length, all seqs are padded to this
BATCH_SIZE = 128 # number of examples per batch
NUM_EPOCHS = 10 # number of epochs to train for (an epoch is one iteration of the entire dataset)
TRAIN_TEST_SPLIT = 0.1 # percentage of data to use for testing
VALIDATION_SPLIT = 0.1 # percentage of training data to use for validation
```

Trained models are stored in the `models` folder. Each model is under its own folder whose folder structure looks as follows:

```python
models
 | - acc%%.%% # where %%.%% represents accuracy on the test set
 |   | - details.yaml # stores training details
 |   | - model.json # stores model architectures
 |   | - tokenizer.json # stores tokenizer embeddings
 |   | - weights.h5 # stores weights for neural conenctions
 | ...
```

### NLP Model CLI

You can also run the NLP model through the command line (given the model exists) by just providing arguments to `serve_model.py`. Example usage is as follows,

```bash
# e.g.
# serve_model.py -m <nameofmodel> -t <threshold> -i <intent>

python serve_model.py -i "I need to make a marketing post"
# Predicting using model acc81.08 with threshold 0.50 on intent "I need to make a marketing post"
# Output -> True

python serve_model.py -i "I want to browse memes"
# Predicting using model acc81.08 with threshold 0.50 on intent "I want to browse memes"
# Output -> False
```

### Using different NLP models on the server.

Currently, the server is running a default model of the `acc81.08` model. This is defined in `server.py` as follows,

```python
if __name__ == '__main__':
    logging.info("Starting server...")
    m = Model("acc81.08", threshold=0.5)
    app.run()
```

You may change the model name and threshold however you may see fit.

### Data Usage

All data found in `data/survey.csv` collected from [this survey](http://bit.ly/reflectdata) that our team sent out in January of 2020. You may use this data to train your own models.