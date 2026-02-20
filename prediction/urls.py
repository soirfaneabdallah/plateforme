from django.urls import path
from . import views

urlpatterns = [
    path('', views.prediction_views, name='predictions'),
    path('predict/', views.detect_anomaly, name='predict'),
    path('confirmation/<int:pk>/', views.anomaly_confirmation, name='anomaly_confirmation'),
    path('classification/<int:pk>/', views.classification_step, name='classification_step'),
    path('camera/', views.camera_page, name='camera_page'),
    path('camera/live/', views.live_camera_feed, name='live_camera_feed'),
    path('camera/predict/', views.capture_and_predict_image, name='capture_and_pred'),
    path("resultats/<int:pk>/", views.resultats, name='resultats')
]




