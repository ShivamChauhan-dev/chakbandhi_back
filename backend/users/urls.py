from django.urls import path

from . import views

urlpatterns = [
    path('', views.UsersListAPIView.as_view()),
    path('<str:username>/', views.UserUpdateAPIView.as_view()),
]
