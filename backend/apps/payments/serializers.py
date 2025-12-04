"""
Serializers REST para la app payments.
Maneja conversión de modelos de pagos y reembolsos a JSON.
"""

from rest_framework import serializers
from .models import Payment, Refund


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer completo para pagos"""
    
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    usuario_email = serializers.EmailField(source='usuario.email', read_only=True)
    boletos_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'usuario', 'usuario_nombre', 'usuario_email',
            'boletos', 'boletos_list', 'monto', 'metodo_pago', 
            'estado', 'transaction_id', 'payment_intent_id',
            'fecha_creacion', 'fecha_completado', 'descripcion',
            'notas_admin'
        ]
        read_only_fields = [
            'id', 'fecha_creacion', 'fecha_completado', 
            'transaction_id', 'payment_intent_id'
        ]
    
    def get_boletos_list(self, obj):
        """Retorna lista simplificada de boletos"""
        return [
            {
                'id': boleto.id,
                'numero': boleto.numero_boleto,
                'rifa': boleto.rifa.titulo,
                'estado': boleto.estado
            }
            for boleto in obj.boletos.all()
        ]


class PaymentListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados de pagos"""
    
    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    cantidad_boletos = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'usuario_nombre', 'monto', 'metodo_pago',
            'estado', 'fecha_creacion', 'cantidad_boletos'
        ]
    
    def get_cantidad_boletos(self, obj):
        """Cuenta la cantidad de boletos"""
        return obj.boletos.count()


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pagos"""
    
    class Meta:
        model = Payment
        fields = [
            'boletos', 'monto', 'metodo_pago', 'descripcion'
        ]
    
    def create(self, validated_data):
        """Crea un nuevo pago"""
        validated_data['usuario'] = self.context['request'].user
        validated_data['estado'] = 'pendiente'
        return super().create(validated_data)
    
    def validate_monto(self, value):
        """Valida que el monto sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0.")
        return value


class RefundSerializer(serializers.ModelSerializer):
    """Serializer completo para reembolsos"""
    
    pago_info = serializers.SerializerMethodField()
    procesado_por_nombre = serializers.CharField(
        source='procesado_por.nombre', 
        read_only=True, 
        allow_null=True
    )
    
    class Meta:
        model = Refund
        fields = [
            'id', 'pago', 'pago_info', 'monto', 'motivo', 
            'razon', 'procesado_por', 'procesado_por_nombre',
            'fecha_solicitud', 'fecha_procesado', 'estado'
        ]
        read_only_fields = [
            'id', 'fecha_solicitud', 'fecha_procesado', 
            'procesado_por'
        ]
    
    def get_pago_info(self, obj):
        """Retorna información básica del pago"""
        return {
            'id': obj.pago.id,
            'monto': str(obj.pago.monto),
            'usuario': obj.pago.usuario.nombre,
            'fecha': obj.pago.fecha_creacion
        }


class RefundListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados de reembolsos"""
    
    usuario_nombre = serializers.CharField(
        source='pago.usuario.nombre', 
        read_only=True
    )
    
    class Meta:
        model = Refund
        fields = [
            'id', 'usuario_nombre', 'monto', 'motivo', 
            'estado', 'fecha_solicitud'
        ]


class RefundCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear solicitudes de reembolso"""
    
    class Meta:
        model = Refund
        fields = ['pago', 'monto', 'motivo', 'razon']
    
    def validate(self, attrs):
        """Valida que el pago sea válido para reembolso"""
        pago = attrs.get('pago')
        monto = attrs.get('monto')
        
        # Verificar que el pago esté completado
        if pago.estado != 'completado':
            raise serializers.ValidationError({
                "pago": "Solo se pueden reembolsar pagos completados."
            })
        
        # Verificar que no exista un reembolso previo
        if hasattr(pago, 'reembolso'):
            raise serializers.ValidationError({
                "pago": "Este pago ya tiene un reembolso asociado."
            })
        
        # Verificar que el monto no exceda el pago original
        if monto > pago.monto:
            raise serializers.ValidationError({
                "monto": "El monto a reembolsar no puede ser mayor al pago original."
            })
        
        return attrs


class PaymentStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de pagos"""
    
    total_pagos = serializers.IntegerField()
    pagos_completados = serializers.IntegerField()
    pagos_pendientes = serializers.IntegerField()
    pagos_fallidos = serializers.IntegerField()
    total_recaudado = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_reembolsado = serializers.DecimalField(max_digits=15, decimal_places=2)
    metodos_pago = serializers.DictField()
