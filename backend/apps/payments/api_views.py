"""
API ViewSets REST para la app payments.
Implementa endpoints completos para gestión de pagos y reembolsos.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count, Q

from .models import Payment, Refund
from .serializers import (
    PaymentSerializer, PaymentListSerializer, PaymentCreateSerializer,
    RefundSerializer, RefundListSerializer, RefundCreateSerializer,
    PaymentStatsSerializer
)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de pagos.
    
    Endpoints:
    - GET /api/payments/ - Lista de pagos
    - POST /api/payments/ - Crear pago
    - GET /api/payments/{id}/ - Detalle de pago
    - PUT /api/payments/{id}/ - Actualizar pago
    - DELETE /api/payments/{id}/ - Eliminar pago
    - GET /api/payments/mis_pagos/ - Pagos del usuario
    - POST /api/payments/{id}/confirmar/ - Confirmar pago
    - POST /api/payments/{id}/cancelar/ - Cancelar pago
    - GET /api/payments/stats/ - Estadísticas de pagos
    """
    
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Retorna serializer apropiado"""
        if self.action == 'list':
            return PaymentListSerializer
        elif self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    def get_queryset(self):
        """Filtra pagos según permisos y parámetros"""
        user = self.request.user
        
        # Admin ve todos los pagos
        if user.is_staff:
            queryset = Payment.objects.all()
        else:
            # Usuarios normales solo ven sus pagos
            queryset = Payment.objects.filter(usuario=user)
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por método de pago
        metodo = self.request.query_params.get('metodo_pago', None)
        if metodo:
            queryset = queryset.filter(metodo_pago=metodo)
        
        # Filtrar por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        if fecha_desde:
            queryset = queryset.filter(fecha_creacion__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_creacion__lte=fecha_hasta)
        
        return queryset
    
    def perform_create(self, serializer):
        """Asigna el usuario al crear el pago"""
        serializer.save(usuario=self.request.user)
    
    @action(detail=False, methods=['get'])
    def mis_pagos(self, request):
        """Retorna pagos del usuario actual"""
        pagos = Payment.objects.filter(usuario=request.user)
        serializer = PaymentListSerializer(pagos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """Confirma un pago (marca como completado)"""
        pago = self.get_object()
        
        # Solo el propietario o admin pueden confirmar
        if pago.usuario != request.user and not request.user.is_staff:
            return Response({
                'error': 'No tienes permiso para esta acción.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if pago.estado not in ['pendiente', 'procesando']:
            return Response({
                'error': 'Solo se pueden confirmar pagos pendientes o en proceso.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Marcar boletos como pagados
        for boleto in pago.boletos.all():
            boleto.estado = 'pagado'
            boleto.save()
        
        pago.estado = 'completado'
        pago.fecha_completado = timezone.now()
        pago.save()
        
        return Response({
            'message': 'Pago confirmado exitosamente.',
            'pago': PaymentSerializer(pago).data
        })
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancela un pago"""
        pago = self.get_object()
        
        # Solo el propietario o admin pueden cancelar
        if pago.usuario != request.user and not request.user.is_staff:
            return Response({
                'error': 'No tienes permiso para esta acción.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if pago.estado not in ['pendiente', 'procesando']:
            return Response({
                'error': 'Solo se pueden cancelar pagos pendientes o en proceso.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Marcar boletos como cancelados
        for boleto in pago.boletos.all():
            boleto.estado = 'cancelado'
            boleto.save()
        
        pago.estado = 'fallido'
        pago.save()
        
        return Response({
            'message': 'Pago cancelado.',
            'pago': PaymentSerializer(pago).data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def stats(self, request):
        """Retorna estadísticas de pagos (solo admin)"""
        # Calcular estadísticas
        total_pagos = Payment.objects.count()
        pagos_completados = Payment.objects.filter(estado='completado').count()
        pagos_pendientes = Payment.objects.filter(estado='pendiente').count()
        pagos_fallidos = Payment.objects.filter(estado='fallido').count()
        
        total_recaudado = Payment.objects.filter(
            estado='completado'
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        total_reembolsado = Refund.objects.filter(
            estado='completado'
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        # Métodos de pago más usados
        metodos_pago = {}
        for metodo, nombre in Payment.METODO_PAGO:
            count = Payment.objects.filter(metodo_pago=metodo).count()
            if count > 0:
                metodos_pago[nombre] = count
        
        stats = {
            'total_pagos': total_pagos,
            'pagos_completados': pagos_completados,
            'pagos_pendientes': pagos_pendientes,
            'pagos_fallidos': pagos_fallidos,
            'total_recaudado': total_recaudado,
            'total_reembolsado': total_reembolsado,
            'metodos_pago': metodos_pago
        }
        
        serializer = PaymentStatsSerializer(stats)
        return Response(serializer.data)


class RefundViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de reembolsos.
    
    Endpoints:
    - GET /api/refunds/ - Lista de reembolsos
    - POST /api/refunds/ - Crear solicitud de reembolso
    - GET /api/refunds/{id}/ - Detalle de reembolso
    - PUT /api/refunds/{id}/ - Actualizar reembolso
    - DELETE /api/refunds/{id}/ - Eliminar reembolso
    - POST /api/refunds/{id}/aprobar/ - Aprobar reembolso (admin)
    - POST /api/refunds/{id}/rechazar/ - Rechazar reembolso (admin)
    - POST /api/refunds/{id}/completar/ - Completar reembolso (admin)
    """
    
    queryset = Refund.objects.all()
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Retorna serializer apropiado"""
        if self.action == 'list':
            return RefundListSerializer
        elif self.action == 'create':
            return RefundCreateSerializer
        return RefundSerializer
    
    def get_queryset(self):
        """Filtra reembolsos según permisos"""
        user = self.request.user
        
        # Admin ve todos los reembolsos
        if user.is_staff:
            queryset = Refund.objects.all()
        else:
            # Usuarios normales solo ven sus reembolsos
            queryset = Refund.objects.filter(pago__usuario=user)
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def aprobar(self, request, pk=None):
        """Aprueba un reembolso (solo admin)"""
        reembolso = self.get_object()
        
        if reembolso.estado != 'solicitado':
            return Response({
                'error': 'Solo se pueden aprobar reembolsos solicitados.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reembolso.estado = 'aprobado'
        reembolso.procesado_por = request.user
        reembolso.fecha_procesado = timezone.now()
        reembolso.save()
        
        return Response({
            'message': 'Reembolso aprobado.',
            'reembolso': RefundSerializer(reembolso).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def rechazar(self, request, pk=None):
        """Rechaza un reembolso (solo admin)"""
        reembolso = self.get_object()
        
        if reembolso.estado != 'solicitado':
            return Response({
                'error': 'Solo se pueden rechazar reembolsos solicitados.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reembolso.estado = 'rechazado'
        reembolso.procesado_por = request.user
        reembolso.fecha_procesado = timezone.now()
        reembolso.save()
        
        return Response({
            'message': 'Reembolso rechazado.',
            'reembolso': RefundSerializer(reembolso).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def completar(self, request, pk=None):
        """Completa un reembolso (marca como procesado)"""
        reembolso = self.get_object()
        
        if reembolso.estado != 'aprobado':
            return Response({
                'error': 'Solo se pueden completar reembolsos aprobados.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Marcar pago como reembolsado
        pago = reembolso.pago
        pago.estado = 'reembolsado'
        pago.save()
        
        # Marcar reembolso como completado
        reembolso.estado = 'completado'
        if not reembolso.fecha_procesado:
            reembolso.fecha_procesado = timezone.now()
        if not reembolso.procesado_por:
            reembolso.procesado_por = request.user
        reembolso.save()
        
        return Response({
            'message': 'Reembolso completado exitosamente.',
            'reembolso': RefundSerializer(reembolso).data
        })
