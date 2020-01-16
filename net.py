# https://www.kaggle.com/jannen/reaching-0-7-fork-from-bilstm-attention-kfold

# load dataset from disk
# load embeddings from disk

# stratified k fold

# set LR (or use Adam or Cyclic CLR)

# Define NN
# define embedding layer -- use pretrained embedding layer
# define simple blstm, hidden size 60
# LR -> 1e-3
# dropout -> 1/4

# training loop, reuse from kfold step