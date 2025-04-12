from django.urls import path
from .views import home, login_view, dashboard, admin_dashboard, register, user_logout, subscribe

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path("logout/", user_logout, name="logout"),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path("subscribe/", subscribe, name="subscribe"),
]
