from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("admin_login/", views.admin_login, name="admin_login"),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path("upload-documents/", views.upload_documents, name="upload_documents"),
    path("login/", views.user_login, name="user_login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.user_logout, name="user_logout"),

]
