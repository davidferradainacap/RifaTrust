"""
Serializers REST para la app raffles.
Maneja conversión de modelos a JSON y validaciones de negocio.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Raffle, Ticket, SponsorshipRequest, OrganizerSponsorRequest, Winner


class TicketSerializer(serializers.ModelSerializer):
    """Serializer para boletos"""

    usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    usuario_email = serializers.EmailField(source='usuario.email', read_only=True)
    rifa_titulo = serializers.CharField(source='rifa.titulo', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'rifa', 'rifa_titulo', 'usuario', 'usuario_nombre',
            'usuario_email', 'numero_boleto', 'fecha_compra',
            'estado', 'codigo_qr'
        ]
        read_only_fields = ['id', 'fecha_compra', 'codigo_qr']


class TicketListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados de boletos"""

    class Meta:
        model = Ticket
        fields = ['id', 'numero_boleto', 'estado', 'fecha_compra']


class RaffleSerializer(serializers.ModelSerializer):
    """Serializer completo para rifas"""

    organizador_nombre = serializers.CharField(source='organizador.nombre', read_only=True)
    organizador_email = serializers.EmailField(source='organizador.email', read_only=True)
    porcentaje_vendido = serializers.FloatField(read_only=True)
    boletos = TicketListSerializer(many=True, read_only=True)
    total_recaudado = serializers.SerializerMethodField()
    tiempo_restante = serializers.SerializerMethodField()
    puede_comprar = serializers.SerializerMethodField()

    class Meta:
        model = Raffle
        fields = [
            'id', 'organizador', 'organizador_nombre', 'organizador_email',
            'titulo', 'descripcion', 'imagen', 'precio_boleto',
            'total_boletos', 'boletos_vendidos', 'porcentaje_vendido',
            'fecha_inicio', 'fecha_sorteo', 'fecha_creacion',
            'fecha_actualizacion', 'estado', 'premio_principal',
            'descripcion_premio', 'imagen_premio', 'valor_premio',
            'documento_legal', 'permite_multiples_boletos',
            'max_boletos_por_usuario', 'fecha_solicitud',
            'revisado_por', 'fecha_revision_aprobacion',
            'comentarios_revision', 'motivo_rechazo', 'motivo_pausa',
            'fecha_pausa', 'revision_admin', 'fecha_revision',
            'nueva_fecha_sorteo', 'boletos', 'total_recaudado',
            'tiempo_restante', 'puede_comprar'
        ]
        read_only_fields = [
            'id', 'fecha_creacion', 'fecha_actualizacion',
            'boletos_vendidos', 'fecha_solicitud', 'fecha_revision_aprobacion',
            'fecha_pausa', 'fecha_revision'
        ]

    def get_total_recaudado(self, obj):
        """Calcula el total recaudado por la rifa"""
        return float(obj.boletos_vendidos * obj.precio_boleto)

    def get_tiempo_restante(self, obj):
        """Calcula tiempo restante hasta el sorteo"""
        if obj.estado in ['finalizada', 'cancelada']:
            return None

        fecha_sorteo = obj.nueva_fecha_sorteo or obj.fecha_sorteo
        delta = fecha_sorteo - timezone.now()

        if delta.total_seconds() < 0:
            return "Vencido"

        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60

        if days > 0:
            return f"{days} días, {hours} horas"
        elif hours > 0:
            return f"{hours} horas, {minutes} minutos"
        else:
            return f"{minutes} minutos"

    def get_puede_comprar(self, obj):
        """Verifica si se pueden comprar boletos (organizadores no pueden comprar)"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Organizadores no pueden comprar boletos
            if request.user.is_authenticated and request.user.rol == 'organizador':
                return False
        return obj.estado == 'activa' and obj.boletos_vendidos < obj.total_boletos

    def validate_fecha_sorteo(self, value):
        """Valida que la fecha de sorteo sea futura"""
        if value <= timezone.now():
            raise serializers.ValidationError("La fecha del sorteo debe ser futura.")
        return value

    def validate_precio_boleto(self, value):
        """Valida que el precio sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value

    def validate(self, attrs):
        """Validaciones cruzadas"""
        # Validar que max_boletos_por_usuario no exceda total_boletos
        if 'max_boletos_por_usuario' in attrs and 'total_boletos' in attrs:
            if attrs['max_boletos_por_usuario'] > attrs['total_boletos']:
                raise serializers.ValidationError({
                    "max_boletos_por_usuario": "No puede ser mayor al total de boletos."
                })

        return attrs


class RaffleListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados de rifas"""

    organizador_nombre = serializers.CharField(source='organizador.nombre', read_only=True)
    porcentaje_vendido = serializers.FloatField(read_only=True)

    class Meta:
        model = Raffle
        fields = [
            'id', 'titulo', 'imagen', 'precio_boleto',
            'total_boletos', 'boletos_vendidos', 'porcentaje_vendido',
            'fecha_sorteo', 'estado', 'premio_principal',
            'organizador_nombre'
        ]


class RaffleCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear rifas"""

    class Meta:
        model = Raffle
        fields = [
            'titulo', 'descripcion', 'imagen', 'precio_boleto',
            'total_boletos', 'fecha_inicio', 'fecha_sorteo',
            'premio_principal', 'descripcion_premio', 'imagen_premio',
            'valor_premio', 'documento_legal', 'permite_multiples_boletos',
            'max_boletos_por_usuario'
        ]

    def create(self, validated_data):
        """Crea una nueva rifa en estado borrador"""
        validated_data['organizador'] = self.context['request'].user
        validated_data['estado'] = 'borrador'
        return super().create(validated_data)


class SponsorshipRequestSerializer(serializers.ModelSerializer):
    """Serializer para solicitudes de patrocinio"""

    sponsor_nombre = serializers.CharField(source='sponsor.nombre', read_only=True)
    rifa_titulo = serializers.CharField(source='rifa.titulo', read_only=True)

    class Meta:
        model = SponsorshipRequest
        fields = [
            'id', 'rifa', 'rifa_titulo', 'sponsor', 'sponsor_nombre',
            'nombre_premio_adicional', 'descripcion_premio', 'valor_premio',
            'imagen_premio', 'nombre_marca', 'logo_marca', 'sitio_web',
            'mensaje_patrocinio', 'estado', 'fecha_solicitud',
            'fecha_respuesta', 'motivo_rechazo'
        ]
        read_only_fields = ['id', 'fecha_solicitud', 'fecha_respuesta', 'estado']


class OrganizerSponsorRequestSerializer(serializers.ModelSerializer):
    """Serializer para solicitudes de organizador a sponsor"""

    organizador_nombre = serializers.CharField(source='organizador.nombre', read_only=True)
    sponsor_nombre = serializers.CharField(source='sponsor.nombre', read_only=True)
    rifa_titulo = serializers.CharField(source='rifa.titulo', read_only=True)

    class Meta:
        model = OrganizerSponsorRequest
        fields = [
            'id', 'rifa', 'rifa_titulo', 'sponsor', 'sponsor_nombre',
            'organizador', 'organizador_nombre', 'mensaje_invitacion',
            'beneficios_ofrecidos', 'estado', 'fecha_solicitud',
            'fecha_respuesta', 'motivo_rechazo', 'propuesta_premio',
            'propuesta_valor'
        ]
        read_only_fields = ['id', 'fecha_solicitud', 'fecha_respuesta', 'organizador']

    def create(self, validated_data):
        """Crea una solicitud de organizador a sponsor"""
        validated_data['organizador'] = self.context['request'].user
        return super().create(validated_data)


class WinnerSerializer(serializers.ModelSerializer):
    """Serializer para ganadores"""

    rifa_titulo = serializers.CharField(source='rifa.titulo', read_only=True)
    boleto_numero = serializers.IntegerField(source='boleto.numero_boleto', read_only=True)
    ganador_nombre = serializers.CharField(source='boleto.usuario.nombre', read_only=True)
    ganador_email = serializers.EmailField(source='boleto.usuario.email', read_only=True)

    class Meta:
        model = Winner
        fields = [
            'id', 'rifa', 'rifa_titulo', 'boleto', 'boleto_numero',
            'ganador_nombre', 'ganador_email', 'fecha_sorteo',
            'verificado', 'premio_entregado', 'fecha_entrega', 'notas',
            'seed_aleatorio', 'timestamp_sorteo', 'algoritmo',
            'hash_verificacion', 'participantes_totales', 'acta_digital'
        ]
        read_only_fields = [
            'id', 'fecha_sorteo', 'seed_aleatorio', 'timestamp_sorteo',
            'algoritmo', 'hash_verificacion', 'participantes_totales',
            'acta_digital'
        ]


class RaffleStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de rifas"""

    total_rifas = serializers.IntegerField()
    rifas_activas = serializers.IntegerField()
    rifas_finalizadas = serializers.IntegerField()
    total_boletos_vendidos = serializers.IntegerField()
    total_recaudado = serializers.DecimalField(max_digits=15, decimal_places=2)
    rifas_pendientes_aprobacion = serializers.IntegerField()
