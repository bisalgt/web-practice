
from django.urls import path
from apps.webapp import views


urlpatterns = [
	path('<int:id>/<slug:slug>/',views.home),
]