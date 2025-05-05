from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import tensorflow as tf
from PIL import Image
import numpy as np
import io

from .utils import treatment_dict
from tensorflow.keras import backend as K
from tensorflow.keras.utils import get_custom_objects

# ✅ Define custom loss function
def focal_loss_fixed(y_true, y_pred, gamma=2., alpha=0.25):
    epsilon = K.epsilon()
    y_pred = K.clip(y_pred, epsilon, 1. - epsilon)
    cross_entropy = -y_true * K.log(y_pred)
    weight = alpha * K.pow(1 - y_pred, gamma)
    loss = weight * cross_entropy
    return K.mean(K.sum(loss, axis=-1))

# ✅ Register custom loss
get_custom_objects()["focal_loss_fixed"] = focal_loss_fixed

# ✅ Class labels
class_labels = ['black_rust', 'brown_rust', 'healthy', 'yellow_rust']

# ✅ Lazy load model
model = None
def get_model():
    global model
    if model is None:
        model = tf.keras.models.load_model(
            "models/wheat_disease_model_final.keras",
            custom_objects={"focal_loss_fixed": focal_loss_fixed}
        )
    return model


@csrf_exempt
def predict_disease(request):
    if request.method == 'POST' and request.FILES.get('image'):
        img_file = request.FILES['image']
        img = Image.open(img_file).resize((224, 224)).convert("RGB")
        img_array = np.expand_dims(np.array(img) / 255.0, axis=0)

        # ✅ Get model only when needed
        model = get_model()

        # Prediction
        prediction = model.predict(img_array)
        class_idx = np.argmax(prediction)
        predicted_class = class_labels[class_idx]

        # Treatment
        treatment = treatment_dict.get(predicted_class, {})

        return JsonResponse({
            "predicted_class": predicted_class,
            "treatment_am": treatment.get("amharic", "N/A"),
            "treatment_en": treatment.get("english", "N/A")
        })

    return JsonResponse({"error": "No image uploaded."}, status=400)