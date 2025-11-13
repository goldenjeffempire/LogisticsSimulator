# Enterprise Logistics Simulation Platform

## Overview
A full-stack, production-ready logistics simulation platform implementing a high-urgency financial resolution workflow. Built with enterprise-grade aesthetics and complex backend logic.

## Technology Stack
- **Backend**: Django + Django REST Framework
- **Real-Time**: Django Channels (WebSockets)
- **Frontend**: HTMX + Alpine.js (SPA-like fluidity)
- **Styling**: Tailwind CSS (Dark Mode Enterprise aesthetic)
- **Database**: SQLite

## Features

### 1. Landing Page (/)
- Parallax animated gradient background
- Interactive US Map (SVG) showing distribution hubs
- Live Status Ticker powered by WebSockets
- Real-time shipment tracking search
- HTMX-powered automatic status updates

### 2. Tracking View (/track/<tracking_number>/)
- Dynamic urgency banners for held shipments
- Multi-line fee breakdown display
- Animated progress bar with real-time updates
- Protected recipient information
- Shipment timeline visualization

### 3. Payment Gateway (/payment/<tracking_number>/)
- Complete fee invoice with line-item breakdown
- 5-minute countdown timer with color escalation
- Simulated 2FA verification modal
- Persistent floating live chat with typing effects
- Context-aware chat responses

### 4. Admin Console (/admin-sim/)
- Hidden administrative interface
- Shipment creation with auto-generated tracking IDs
- Dynamic fee management (Add/Edit/Delete line items)
- Fee requirement toggle
- Real-time total calculation
- CRUD operations via DRF REST API

## Data Model

### Shipment Model
- `tracking_number`: Auto-generated (US-9000-TKG-XXXXXX)
- `owner_name`: Recipient details
- `fee_required`: Boolean hold trigger
- `fees`: JSONField array of line-item fees
- `total_amount`: Auto-calculated sum of fees (default $80.00)
- `status`: Current shipment status
- `origin`/`destination`: Route information

## API Endpoints (Django REST Framework)

- `GET /api/shipments/` - List all shipments
- `POST /api/shipments/` - Create new shipment
- `GET /api/shipments/{id}/` - Retrieve shipment details
- `PATCH /api/shipments/{id}/` - Update shipment
- `DELETE /api/shipments/{id}/` - Delete shipment

**Security**: Session authentication with CSRF protection for admin operations.

## Aesthetic Details

### Dark Mode Enterprise Theme
- Deep Charcoal/Navy base colors
- Electric Cyan (#06b6d4) accents
- Glassmorphism effects with backdrop blur
- Complex layered shadows
- Fluid CSS transitions and micro-animations
- Pulsing urgency indicators

## WebSocket Integration
- Live status ticker on landing page
- Real-time updates via Django Channels
- Automatic reconnection handling

## Sample Data
Two pre-loaded shipments for testing:
- US-9000-TKG-857531 (John Smith)
- US-9000-TKG-705968 (Sarah Johnson)

## Development
- Run server: `daphne -b 0.0.0.0 -p 5000 logistics_platform.asgi:application`
- Migrations: `python manage.py makemigrations && python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`

## Notes
This is a simulation/demonstration platform. In production, admin APIs would require proper authentication (TokenAuthentication/IsAdminUser). Current implementation uses SessionAuthentication with CSRF protection for browser-based admin operations while allowing public read access for tracking functionality.
