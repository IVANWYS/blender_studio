from django.urls import path
from . import views

urlpatterns = [
    path('', views.files_upload, name='files_upload'),
    path('send_files', views.send_files, name='send_files'),
]
