from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/count/', views.notification_count, name='notification_count'),
    path('notifications/api/list/', views.notifications_api_list, name='notifications_api_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),

    # Email Confirmation
    path('email-confirmation-sent/', views.email_confirmation_sent_view, name='email_confirmation_sent'),
    path('confirm-email/<str:token>/', views.confirm_email_view, name='confirm_email'),
    path('resend-confirmation/', views.resend_confirmation_email_view, name='resend_confirmation'),

    # Password Reset - HTML Views
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset-sent/', views.password_reset_sent_view, name='password_reset_sent'),
    path('reset-password/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),

    # Password Reset - API
    path('api/password-reset/request/', views.request_password_reset, name='api_password_reset_request'),
    path('api/password-reset/verify/<str:token>/', views.verify_reset_token, name='api_password_reset_verify'),
    path('api/password-reset/confirm/<str:token>/', views.confirm_password_reset, name='api_password_reset_confirm'),
]
