#urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('submit-loan-application/', views.submit_application, name='submit-application'),
]