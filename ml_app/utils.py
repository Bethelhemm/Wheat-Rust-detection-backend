import tensorflow as tf

def convert_keras_to_tflite(keras_model_path: str, tflite_model_path: str):
    """
    Converts a Keras model (.h5 or .keras) to TensorFlow Lite format (.tflite).

    Args:
        keras_model_path (str): Path to the input Keras model file.
        tflite_model_path (str): Path where the output TFLite model will be saved.
    """
    # Load the Keras model
    model = tf.keras.models.load_model(keras_model_path)

    # Create a TFLiteConverter object from the Keras model
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # Convert the model to TFLite format
    tflite_model = converter.convert()

    # Save the converted model to disk
    with open(tflite_model_path, "wb") as f:
        f.write(tflite_model)
