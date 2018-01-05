from django.conf.urls import include, url
from telle import views

urlpatterns = [
    url(r'^', include('telle.urls')),
    url(r'^$', views.home),
]