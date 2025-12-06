
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('book/<int:slot_id>/', views.book_slot, name='book_slot'),
    path('mybookings/', views.my_bookings, name='my_bookings'),
]
