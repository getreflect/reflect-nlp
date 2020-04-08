MODEL=$1

tensorflowjs_converter --input_format keras \
                        models/$1/weights.h5 \
                        converted_models/$1

cp models/$1/tokenizer.json converted_models/$1/tokenizer.json