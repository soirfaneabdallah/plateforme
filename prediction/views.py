from django.shortcuts import render, redirect, get_object_or_404
from .forms import PredictionForm
from .models import Predictions
from django.contrib.auth.decorators import login_required
import tensorflow as tf
import cv2
import tempfile
from tensorflow.keras.preprocessing import image as tf_image
import numpy as np
from django.http import StreamingHttpResponse
# Create your views here.

def prediction_views(request):
    
    return render(request, 'prediction/index.html')

def prepare_image(img_path, target_size):
    img = tf_image.load_img(img_path, target_size=(target_size,target_size))
    img_array = tf_image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  
    img_array /= 255.0  
    return img_array

@login_required
def detect_anomaly(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        prediction = Predictions(utilisateur=request.user, image=image)
        prediction.save()

        # Préparation de l'image pour la détection d'anomalie
        img_path = prediction.image.path
        img_array = prepare_image(img_path = img_path, target_size = 225)
        # Charger le modèle de détection d'anomalies
        model = tf.keras.models.load_model('model/classification1.keras')
        #result = model.predict(image)[0][0]
        predicted_class = model.predict(img_array)
        result = np.argmax(predicted_class, axis=1)
        # Résultat de la détection d'anomalie
        prediction.anomalie_detectee = result[0] < 0.7
        prediction.save()

        return redirect('anomaly_confirmation', pk=prediction.pk)
    return render(request, 'prediction/prediction.html')

@login_required
def anomaly_confirmation(request, pk):
    prediction = get_object_or_404(Predictions, pk = pk)
    if request.method == 'POST':
        form = PredictionForm(request.POST, instance=prediction)
        if form.is_valid():
            form.save()
            return redirect('classification_step', pk=prediction.pk)
    else:
        form = PredictionForm(instance=prediction)
    return render(request, 'prediction/anomaly_confirmation.html', {'form': form, 'prediction': prediction})

@login_required
def classification_step(request, pk):
    list_name = ['Canette','Organique','Plastique','Textile','Verre']
    prediction = get_object_or_404(Predictions, pk = pk)

    if request.method == 'POST':
        selected_class = request.POST.get('classe_corrigee')
        if selected_class:
            prediction.classe_corrigee = selected_class
            prediction.save()
            prediction.update_image_path()
            return redirect('resultats', pk=prediction.pk)

    # Afficher le résultat de la classification initiale
    model = tf.keras.models.load_model('model/classification1.keras')
    img_path = prediction.image.path
    img_array = prepare_image(img_path = img_path, target_size = 225) 
    predicted_class = model.predict(img_array)
    y_pred = np.argmax(predicted_class, axis=1)
    prediction.classe = list_name[y_pred[0]]
    prediction.precision = np.max(predicted_class[0]*100) 
    prediction.save()
    
    return render(request, 'prediction/classification.html', {'prediction': prediction})

def resultats(request, pk):
    prediction = get_object_or_404(Predictions, pk = pk)
    return render(request, 'prediction/resultats.html', {"prediction": prediction})

model = tf.keras.models.load_model('model/classification1.keras') 

def gen(camera):
    """Stream le flux de la caméra en direct."""
    while True:
        ret, frame = camera.read()
        if not ret:
            break

        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def live_camera_feed(request):
    """Vue pour le flux vidéo en direct."""
    camera = cv2.VideoCapture(0) 
    return StreamingHttpResponse(gen(camera), content_type='multipart/x-mixed-replace; boundary=frame')

def capture_and_predict_image(request):
    if request.method == 'GET':
        # Capture de l'image depuis la caméra
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()
        camera.release()

        if ret:
            # Sauvegarder l'image capturée dans un fichier temporaire
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            cv2.imwrite(temp_file.name, frame)
            
            # Créer une instance Prediction en utilisant le chemin du fichier temporaire
            prediction = Predictions(utilisateur=request.user)
            prediction.image.save(f"{request.user.username}_capture.jpg", open(temp_file.name, 'rb'))
            prediction.save()

            # Préparer l'image pour la détection d'anomalie
            image = cv2.imread(temp_file.name)
            image = cv2.resize(image, (225, 225))
            image = np.expand_dims(image, axis=0)

            # Charger le modèle de détection d'anomalies
            model = tf.keras.models.load_model('model/classification1.keras')
            predicted_class = model.predict(image)
            result = np.argmax(predicted_class, axis=1)

            # Résultat de la détection d'anomalie
            prediction.anomalie_detectee = result[0] < 0.7  
            prediction.save()

            return redirect('anomaly_confirmation', pk=prediction.pk)
    return render(request, 'prediction/live_capture.html')





def camera_page(request):
    """Page HTML pour afficher le flux de la caméra et faire la prédiction."""
    return render(request, 'prediction/live_capture.html')