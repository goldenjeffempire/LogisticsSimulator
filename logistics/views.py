from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets, permissions, authentication
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Shipment
from .serializers import ShipmentSerializer
import json

def landing_page(request):
    return render(request, 'landing.html')

def track_shipment(request, tracking_number):
    shipment = get_object_or_404(Shipment, tracking_number=tracking_number)
    return render(request, 'track.html', {'shipment': shipment})

def payment_page(request, tracking_number):
    shipment = get_object_or_404(Shipment, tracking_number=tracking_number)
    return render(request, 'payment.html', {'shipment': shipment})

@ensure_csrf_cookie
def admin_console(request):
    shipments = list(Shipment.objects.all().values())
    return render(request, 'admin_console.html', {'shipments': json.dumps(shipments, default=str)})

class ShipmentViewSet(viewsets.ModelViewSet):
    """
    Shipment management API with read-only public access and authenticated mutations.
    Public users can view shipments, but only authenticated sessions can create/update/delete.
    """
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    authentication_classes = [authentication.SessionAuthentication]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.AllowAny()]
