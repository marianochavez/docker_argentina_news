from django.urls import path
from .views import home, city_delete

urlpatterns = [
    path('', home, name="home"),
    path('city-delete/<int:city_id>',city_delete,name="city_delete"),
]