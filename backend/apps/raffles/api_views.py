"""
API ViewSets REST para la app raffles.
Implementa endpoints completos para gestión de rifas, boletos, patrocinios y sorteos.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Sum, Count
from django.shortcuts import get_object_or_404
import random
import hashlib
import time

from .models import Raffle, Ticket, SponsorshipRequest, OrganizerSponsorRequest, Winner
from .serializers import (
    RaffleSerializer, RaffleListSerializer, RaffleCreateSerializer,
    TicketSerializer, TicketListSerializer,
    SponsorshipRequestSerializer, OrganizerSponsorRequestSerializer,
    WinnerSerializer, RaffleStatsSerializer
)


class RaffleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de rifas.
    
    Endpoints:
    - GET /api/raffles/ - Lista de rifas
    - POST /api/raffles/ - Crear rifa
    - GET /api/raffles/{id}/ - Detalle de rifa
    - PUT /api/raffles/{id}/ - Actualizar rifa
    - DELETE /api/raffles/{id}/ - Eliminar rifa
    - GET /api/raffles/activas/ - Rifas activas
    - GET /api/raffles/mis_rifas/ - Rifas del usuario
    - POST /api/raffles/{id}/solicitar_aprobacion/ - Solicitar aprobación
    - POST /api/raffles/{id}/aprobar/ - Aprobar rifa (admin)
    - POST /api/raffles/{id}/rechazar/ - Rechazar rifa (admin)
    - POST /api/raffles/{id}/activar/ - Activar rifa
    - POST /api/raffles/{id}/pausar/ - Pausar rifa
    - POST /api/raffles/{id}/realizar_sorteo/ - Realizar sorteo
    - GET /api/raffles/stats/ - Estadísticas generales
    """
    
    queryset = Raffle.objects.all()
    serializer_class = RaffleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """Retorna serializer apropiado"""
        if self.action == 'list':
            return RaffleListSerializer
        elif self.action == 'create':
            return RaffleCreateSerializer
        return RaffleSerializer
    
    def get_permissions(self):
        """Define permisos según la acción"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def get_queryset(self):
        """Filtra rifas según parámetros"""
        queryset = Raffle.objects.all()
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por organizador
        organizador_id = self.request.query_params.get('organizador', None)
        if organizador_id:
            queryset = queryset.filter(organizador_id=organizador_id)
        
        # Búsqueda
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) | 
                Q(descripcion__icontains=search) |
                Q(premio_principal__icontains=search)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Asigna el organizador al crear"""
        serializer.save(organizador=self.request.user)
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Retorna rifas activas"""
        rifas = Raffle.objects.filter(estado='activa')
        serializer = RaffleListSerializer(rifas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mis_rifas(self, request):
        """Retorna rifas del usuario actual"""
        rifas = Raffle.objects.filter(organizador=request.user)
        serializer = RaffleListSerializer(rifas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def solicitar_aprobacion(self, request, pk=None):
        """Solicita aprobación de una rifa"""
        rifa = self.get_object()
        
        if rifa.organizador != request.user:
            return Response({
                'error': 'No tienes permiso para esta acción.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if rifa.estado != 'borrador':
            return Response({
                'error': 'Solo se pueden enviar rifas en estado borrador.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        rifa.estado = 'pendiente_aprobacion'
        rifa.fecha_solicitud = timezone.now()
        rifa.save()
        
        return Response({
            'message': 'Rifa enviada para aprobación.',
            'rifa': RaffleSerializer(rifa).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def aprobar(self, request, pk=None):
        """Aprueba una rifa (solo admin)"""
        rifa = self.get_object()
        
        if rifa.estado != 'pendiente_aprobacion':
            return Response({
                'error': 'Solo se pueden aprobar rifas pendientes.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        rifa.estado = 'aprobada'
        rifa.revisado_por = request.user
        rifa.fecha_revision_aprobacion = timezone.now()
        rifa.comentarios_revision = request.data.get('comentarios', '')
        rifa.save()
        
        return Response({
            'message': 'Rifa aprobada exitosamente.',
            'rifa': RaffleSerializer(rifa).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def rechazar(self, request, pk=None):
        """Rechaza una rifa (solo admin)"""
        rifa = self.get_object()
        
        if rifa.estado != 'pendiente_aprobacion':
            return Response({
                'error': 'Solo se pueden rechazar rifas pendientes.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        motivo = request.data.get('motivo_rechazo')
        if not motivo:
            return Response({
                'error': 'Debe proporcionar un motivo de rechazo.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        rifa.estado = 'rechazada'
        rifa.revisado_por = request.user
        rifa.fecha_revision_aprobacion = timezone.now()
        rifa.motivo_rechazo = motivo
        rifa.save()
        
        return Response({
            'message': 'Rifa rechazada.',
            'rifa': RaffleSerializer(rifa).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def activar(self, request, pk=None):
        """Activa una rifa aprobada"""
        rifa = self.get_object()
        
        if rifa.organizador != request.user and not request.user.is_staff:
            return Response({
                'error': 'No tienes permiso para esta acción.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if rifa.estado != 'aprobada':
            return Response({
                'error': 'Solo se pueden activar rifas aprobadas.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        rifa.estado = 'activa'
        rifa.save()
        
        return Response({
            'message': 'Rifa activada exitosamente.',
            'rifa': RaffleSerializer(rifa).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def pausar(self, request, pk=None):
        """Pausa una rifa (solo admin)"""
        rifa = self.get_object()
        
        if rifa.estado != 'activa':
            return Response({
                'error': 'Solo se pueden pausar rifas activas.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        motivo = request.data.get('motivo_pausa')
        if not motivo:
            return Response({
                'error': 'Debe proporcionar un motivo de pausa.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        rifa.estado = 'pausada'
        rifa.motivo_pausa = motivo
        rifa.fecha_pausa = timezone.now()
        rifa.save()
        
        return Response({
            'message': 'Rifa pausada.',
            'rifa': RaffleSerializer(rifa).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def realizar_sorteo(self, request, pk=None):
        """Realiza el sorteo de una rifa"""
        rifa = self.get_object()
        
        if rifa.organizador != request.user and not request.user.is_staff:
            return Response({
                'error': 'No tienes permiso para esta acción.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if rifa.estado not in ['activa', 'cerrada']:
            return Response({
                'error': 'Solo se pueden sortear rifas activas o cerradas.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que haya boletos vendidos
        boletos_pagados = Ticket.objects.filter(rifa=rifa, estado='pagado')
        if not boletos_pagados.exists():
            return Response({
                'error': 'No hay boletos pagados para sortear.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que no tenga ganador
        if hasattr(rifa, 'ganador'):
            return Response({
                'error': 'Esta rifa ya tiene un ganador.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Realizar sorteo
        timestamp = int(time.time())
        seed = hashlib.sha256(f"{rifa.id}{timestamp}".encode()).hexdigest()
        random.seed(seed)
        
        boleto_ganador = random.choice(boletos_pagados)
        boleto_ganador.estado = 'ganador'
        boleto_ganador.save()
        
        # Crear registro de ganador
        acta = f"""
ACTA DIGITAL DE SORTEO
Rifa: {rifa.titulo}
Fecha: {timezone.now()}
Algoritmo: SHA256 + Random Seed
Seed Aleatorio: {seed}
Timestamp: {timestamp}
Total Participantes: {boletos_pagados.count()}
Boleto Ganador: #{boleto_ganador.numero_boleto}
Usuario Ganador: {boleto_ganador.usuario.nombre}
        """
        
        winner = Winner.objects.create(
            rifa=rifa,
            boleto=boleto_ganador,
            seed_aleatorio=seed,
            timestamp_sorteo=timestamp,
            participantes_totales=boletos_pagados.count(),
            acta_digital=acta
        )
        
        rifa.estado = 'finalizada'
        rifa.save()
        
        return Response({
            'message': 'Sorteo realizado exitosamente.',
            'winner': WinnerSerializer(winner).data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retorna estadísticas generales de rifas"""
        stats = {
            'total_rifas': Raffle.objects.count(),
            'rifas_activas': Raffle.objects.filter(estado='activa').count(),
            'rifas_finalizadas': Raffle.objects.filter(estado='finalizada').count(),
            'total_boletos_vendidos': Ticket.objects.filter(estado='pagado').count(),
            'total_recaudado': Ticket.objects.filter(
                estado='pagado'
            ).aggregate(
                total=Sum('rifa__precio_boleto')
            )['total'] or 0,
            'rifas_pendientes_aprobacion': Raffle.objects.filter(
                estado='pendiente_aprobacion'
            ).count()
        }
        
        serializer = RaffleStatsSerializer(stats)
        return Response(serializer.data)


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gestión de boletos (solo lectura via API).
    
    Endpoints:
    - GET /api/tickets/ - Lista de boletos
    - GET /api/tickets/{id}/ - Detalle de boleto
    - GET /api/tickets/mis_boletos/ - Boletos del usuario
    """
    
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """Retorna serializer apropiado"""
        if self.action == 'list':
            return TicketListSerializer
        return TicketSerializer
    
    def get_queryset(self):
        """Filtra boletos según parámetros"""
        queryset = Ticket.objects.all()
        
        # Filtrar por rifa
        rifa_id = self.request.query_params.get('rifa', None)
        if rifa_id:
            queryset = queryset.filter(rifa_id=rifa_id)
        
        # Filtrar por usuario
        usuario_id = self.request.query_params.get('usuario', None)
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mis_boletos(self, request):
        """Retorna boletos del usuario actual"""
        boletos = Ticket.objects.filter(usuario=request.user)
        serializer = TicketSerializer(boletos, many=True)
        return Response(serializer.data)


class SponsorshipRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet para solicitudes de patrocinio de sponsors a rifas.
    
    Endpoints:
    - GET /api/sponsorship-requests/ - Lista de solicitudes
    - POST /api/sponsorship-requests/ - Crear solicitud
    - GET /api/sponsorship-requests/{id}/ - Detalle
    - PUT /api/sponsorship-requests/{id}/ - Actualizar
    - DELETE /api/sponsorship-requests/{id}/ - Eliminar
    - POST /api/sponsorship-requests/{id}/aceptar/ - Aceptar (organizador)
    - POST /api/sponsorship-requests/{id}/rechazar/ - Rechazar (organizador)
    """
    
    queryset = SponsorshipRequest.objects.all()
    serializer_class = SponsorshipRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra solicitudes según usuario y parámetros"""
        user = self.request.user
        queryset = SponsorshipRequest.objects.all()
        
        # Si es organizador, ver solicitudes de sus rifas
        if user.rol == 'organizador':
            queryset = queryset.filter(rifa__organizador=user)
        # Si es sponsor, ver sus solicitudes
        elif user.rol == 'sponsor':
            queryset = queryset.filter(sponsor=user)
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset
    
    def perform_create(self, serializer):
        """Asigna el sponsor al crear"""
        serializer.save(sponsor=self.request.user)
    
    @action(detail=True, methods=['post'])
    def aceptar(self, request, pk=None):
        """Acepta una solicitud de patrocinio (organizador)"""
        solicitud = self.get_object()
        
        if solicitud.rifa.organizador != request.user:
            return Response({
                'error': 'Solo el organizador puede aceptar solicitudes.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if solicitud.estado != 'pendiente':
            return Response({
                'error': 'Solo se pueden aceptar solicitudes pendientes.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        solicitud.estado = 'aceptada'
        solicitud.fecha_respuesta = timezone.now()
        solicitud.save()
        
        return Response({
            'message': 'Solicitud aceptada.',
            'solicitud': SponsorshipRequestSerializer(solicitud).data
        })
    
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """Rechaza una solicitud de patrocinio (organizador)"""
        solicitud = self.get_object()
        
        if solicitud.rifa.organizador != request.user:
            return Response({
                'error': 'Solo el organizador puede rechazar solicitudes.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        motivo = request.data.get('motivo_rechazo')
        if not motivo:
            return Response({
                'error': 'Debe proporcionar un motivo de rechazo.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        solicitud.estado = 'rechazada'
        solicitud.fecha_respuesta = timezone.now()
        solicitud.motivo_rechazo = motivo
        solicitud.save()
        
        return Response({
            'message': 'Solicitud rechazada.',
            'solicitud': SponsorshipRequestSerializer(solicitud).data
        })


class OrganizerSponsorRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet para solicitudes de organizadores a sponsors.
    """
    
    queryset = OrganizerSponsorRequest.objects.all()
    serializer_class = OrganizerSponsorRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra solicitudes según usuario"""
        user = self.request.user
        queryset = OrganizerSponsorRequest.objects.all()
        
        # Si es organizador, ver sus solicitudes enviadas
        if user.rol == 'organizador':
            queryset = queryset.filter(organizador=user)
        # Si es sponsor, ver invitaciones recibidas
        elif user.rol == 'sponsor':
            queryset = queryset.filter(sponsor=user)
        
        return queryset


class WinnerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ganadores (solo lectura).
    
    Endpoints:
    - GET /api/winners/ - Lista de ganadores
    - GET /api/winners/{id}/ - Detalle de ganador
    """
    
    queryset = Winner.objects.all()
    serializer_class = WinnerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
