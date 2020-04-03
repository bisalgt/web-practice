
from django.urls import path
from apps.webapp import views2


urlpatterns = [
	path('suggestor/',views2.home),
]