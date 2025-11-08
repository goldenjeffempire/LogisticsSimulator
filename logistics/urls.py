from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('track/', views.track_shipment, name='track_shipment'),
    path('tracking/<str:tracking_id>/payment/', views.payment_gateway, name='payment_gateway'),
    path('tracking/<str:tracking_id>/process-payment/', views.process_payment, name='process_payment'),
    path('tracking/<str:tracking_id>/confirmation/', views.tracking_confirmation, name='tracking_confirmation'),
    path('admin-console/', views.admin_console, name='admin_console'),
    path('chat/', views.chat_interface, name='chat'),
]
