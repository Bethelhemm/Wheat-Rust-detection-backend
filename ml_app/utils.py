treatment_dict = {
    "black_rust": {
        "amharic": "እንደ Propiconazole ያሉ ፀረ-ተባይ መድሃኒቶችን ይጠቀሙ. ኢንፌክሽንን ለመቀነስ ሰብሎችን ማዞር።",
        "english": "Use fungicides like Propiconazole. Rotate crops to reduce infection."
    },
    "brown_rust": {
        "amharic": "እንደ Triadimefon ወይም Mancozeb ያሉ ፀረ-ተባይ መድሃኒቶችን ይጠቀሙ. በመጀመሪያው የኢንፌክሽን ምልክት ላይ ቀደም ብለው ያመልክቱ።",
        "english": "Use fungicides like Triadimefon or Mancozeb. Apply early at the first sign of infection."
    },
    "yellow_rust": {
        "amharic": "እንደ tebuconazole ያሉ ፀረ-ፈንገስ መድሃኒቶችን ይጠቀሙ. ከፍተኛ እርጥበትን ያስወግዱ እና በየጊዜው ይቆጣጠሩ.።",
        "english": "Use fungicides such as tebuconazole. Avoid high humidity and monitor regularly."
    },
    "healthy": {
        "amharic": "ስንዴው ጤናማ ነው. መከታተልዎን ይቀጥሉ እና ምርጥ የግብርና ልምዶችን ይጠቀሙ።።",
        "english": "The wheat is healthy. Keep monitoring and use best farming practices."
    }
}

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
