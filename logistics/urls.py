from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'shipments', views.ShipmentViewSet)

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('track/<str:tracking_number>/', views.track_shipment, name='track'),
    path('payment/<str:tracking_number>/', views.payment_page, name='payment'),
    path('admin-sim/', views.admin_console, name='admin_console'),
    path('api/', include(router.urls)),
]
