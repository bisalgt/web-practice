
from django.urls import path
from apps.webapp import views


urlpatterns = [
	path('suggestor/',views.home),
]