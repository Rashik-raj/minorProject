from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = "home"),
    path('summary/', views.get_summary, name = "summarize"),
]
