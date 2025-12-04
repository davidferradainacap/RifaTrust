from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<str:ticket_ids>/', views.process_payment_view, name='process_payment'),
    path('success/<int:payment_id>/', views.payment_success_view, name='payment_success'),
    path('failed/<int:payment_id>/', views.payment_failed_view, name='payment_failed'),
]
