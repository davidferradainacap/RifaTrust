from django.urls import path
from . import views

app_name = 'raffles'

urlpatterns = [
    path('', views.raffles_list_view, name='list'),
    path('<int:pk>/', views.raffle_detail_view, name='detail'),
    path('<int:pk>/roulette/', views.roulette_view, name='roulette'),
    path('<int:pk>/perform-draw/', views.perform_raffle_draw, name='perform_draw'),
    path('<int:pk>/check-winner/', views.check_raffle_winner, name='check_winner'),
    path('<int:pk>/select-winner/', views.select_winner_view, name='select_winner'),
    path('<int:pk>/acta-sorteo/', views.acta_sorteo_view, name='acta_sorteo'),
    path('create/', views.create_raffle_view, name='create'),
    path('<int:pk>/edit/', views.edit_raffle_view, name='edit'),
    path('<int:raffle_id>/buy/', views.buy_ticket_view, name='buy_ticket'),
    path('participant/dashboard/', views.participant_dashboard_view, name='participant_dashboard'),
    path('organizer/dashboard/', views.organizer_dashboard_view, name='organizer_dashboard'),
    path('sponsor/dashboard/', views.sponsor_dashboard_view, name='sponsor_dashboard'),
    
    # Sponsorship URLs (Sponsor → Organizador)
    path('<int:pk>/sponsor-request/', views.create_sponsorship_request_view, name='create_sponsorship_request'),
    path('sponsorship/<int:pk>/', views.sponsorship_request_detail_view, name='sponsorship_request_detail'),
    path('sponsorship/<int:pk>/accept/', views.accept_sponsorship_request_view, name='accept_sponsorship'),
    path('sponsorship/<int:pk>/reject/', views.reject_sponsorship_request_view, name='reject_sponsorship'),
    
    # Organizer → Sponsor URLs
    path('browse-sponsors/', views.browse_sponsors_view, name='browse_sponsors'),
    path('invite-sponsor/<int:sponsor_id>/', views.send_sponsor_invitation_view, name='send_sponsor_invitation'),
    path('organizer-request/<int:pk>/', views.organizer_request_detail_view, name='organizer_request_detail'),
    path('organizer-request/<int:pk>/accept/', views.accept_organizer_request_view, name='accept_organizer_request'),
    path('organizer-request/<int:pk>/reject/', views.reject_organizer_request_view, name='reject_organizer_request'),
]
