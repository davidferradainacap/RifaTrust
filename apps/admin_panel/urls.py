from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.admin_dashboard_view, name='dashboard'),
    path('users/', views.users_management_view, name='users_management'),
    path('users/<int:user_id>/profile/', views.user_profile_view, name='user_profile'),
    path('raffles/', views.raffles_management_view, name='raffles_management'),
    path('payments/', views.payments_management_view, name='payments_management'),
    path('audit-logs/', views.audit_logs_view, name='audit_logs'),
    path('audit-logs/<int:log_id>/details/', views.audit_log_details, name='audit_log_details'),
    path('export/users/excel/', views.export_users_excel, name='export_users_excel'),
    path('export/raffles/pdf/', views.export_raffles_pdf, name='export_raffles_pdf'),
    # Gestión de Sponsors
    path('sponsors/approve/<int:user_id>/', views.approve_sponsor_ajax, name='approve_sponsor'),
    path('sponsors/reject/<int:user_id>/', views.reject_sponsor_ajax, name='reject_sponsor'),
    
    # Gestión de Usuarios (AJAX)
    path('users/<int:user_id>/change-role/', views.change_user_role_ajax, name='change_user_role'),
    path('users/<int:user_id>/suspend/', views.suspend_user_ajax, name='suspend_user'),
    path('users/<int:user_id>/activate/', views.activate_user_ajax, name='activate_user'),
    path('users/<int:user_id>/delete/', views.delete_user_ajax, name='delete_user'),
    
    # Gestión de Rifas (AJAX)
    path('raffles/<int:raffle_id>/cancel/', views.cancel_raffle_ajax, name='cancel_raffle'),
    path('raffles/<int:raffle_id>/force-winner/', views.force_winner_ajax, name='force_winner'),
    path('raffles/<int:raffle_id>/delete/', views.delete_raffle_ajax, name='delete_raffle'),
    
    # Gestión de Pagos (AJAX)
    path('payments/<int:payment_id>/refund/', views.refund_payment_ajax, name='refund_payment'),
    
    # Rifas Pausadas
    path('rifas-pausadas/', views.rifas_pausadas_view, name='rifas_pausadas'),
    path('rifas-pausadas/<int:rifa_id>/revisar/', views.revisar_rifa_pausada, name='revisar_rifa_pausada'),

    # Rifas Pendientes de Aprobación
    path('rifas-pendientes/', views.rifas_pendientes_view, name='rifas_pendientes'),
    path('rifas-pendientes/<int:rifa_id>/revisar/', views.revisar_rifa_pendiente, name='revisar_pendiente'),
]
