MODEL=$1

tensorflowjs_converter --input_format keras \
                        models/$1/weights.h5 \
                        converted_models/$1