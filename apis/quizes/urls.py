from django.urls import path
from apis.quizes import views



urlpatterns = [

	path('', views.suggestor),

]