# ============================================================================
# MÓDULO DE PAGOS - VIEWS
# ============================================================================
# Gestiona el procesamiento de pagos para compra de boletos de rifas
# Integración con Stripe como procesador principal
# Soporta múltiples métodos de pago y genera notificaciones
# ============================================================================

# === IMPORTACIONES DJANGO ===
from django.shortcuts import render, redirect, get_object_or_404
# - render: renderiza templates con contexto
# - redirect: redirige a otra vista por nombre o URL
# - get_object_or_404: obtiene objeto o retorna 404

from django.contrib.auth.decorators import login_required
# - Decorador que requiere autenticación para acceder a la vista

from django.contrib import messages
# - Sistema de mensajes flash (success, error, warning, info)

from django.conf import settings
# - Acceso a configuraciones del proyecto (settings.py)

# === IMPORTACIONES DE MODELOS ===
from apps.raffles.models import Ticket
# - Modelo Ticket para validar boletos reservados

from .models import Payment
# - Modelo Payment para registrar transacciones

# === SEGURIDAD ===
from apps.core.safe_errors import handle_exception_safely, get_error_message

# === IMPORTACIONES EXTERNAS ===
import uuid
# - Generador de identificadores únicos universales (UUID4)
# - Usado para transaction_id únicos

# NOTA: Stripe ha sido deshabilitado para usar modo de simulación completa
# Para habilitar pagos reales en el futuro, descomentar las siguientes líneas:
# import stripe
# stripe.api_key = settings.STRIPE_SECRET_KEY

# ============================================================================
# VISTA: process_payment_view
# ============================================================================
# Procesa el pago de uno o múltiples boletos reservados
#
# URL: /payments/process/<ticket_ids>/
# Método: GET (formulario), POST (procesamiento)
# Autenticación: Requerida (@login_required)
#
# Flujo:
# 1. Validar que los boletos existan y pertenezcan al usuario
# 2. Calcular monto total a cobrar
# 3. Crear registro de Payment con estado 'procesando'
# 4. Integrar con Stripe para cobrar
# 5. Actualizar estados de Payment y Tickets según resultado
# 6. Notificar al usuario del resultado
#
# Parámetros URL:
# - ticket_ids: String con IDs separados por comas (ej: "1,2,3")
#
# Redirecciones:
# - Éxito: payment_success_view
# - Fallo: payment_failed_view
# - Sin boletos válidos: dashboard
# ============================================================================
@login_required
def process_payment_view(request, ticket_ids):
    # === PASO 1: PARSEAR Y VALIDAR TICKET IDS ===
    # Convertir string "1,2,3" a lista de enteros [1, 2, 3]
    ticket_id_list = [int(tid) for tid in ticket_ids.split(',')]

    # === PASO 2: OBTENER BOLETOS RESERVADOS ===
    # Filtros críticos:
    # - id__in: Solo los IDs especificados
    # - usuario=request.user: Solo boletos del usuario actual (seguridad)
    # - estado='reservado': Solo boletos no pagados aún
    tickets = Ticket.objects.filter(
        id__in=ticket_id_list,
        usuario=request.user,
        estado='reservado'
    )

    # === PASO 3: VALIDAR QUE EXISTAN BOLETOS ===
    if not tickets.exists():
        messages.error(request, 'No se encontraron boletos válidos.')
        return redirect('dashboard')

    # === PASO 4: CALCULAR MONTO TOTAL ===
    # Suma el precio_boleto de cada rifa asociada a los tickets
    # Ejemplo: 3 boletos de $1000 = $3000
    total_amount = sum(ticket.rifa.precio_boleto for ticket in tickets)

    # === PASO 5: PROCESAR FORMULARIO (POST) ===
    if request.method == 'POST':
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Obtener método de pago seleccionado por usuario
            metodo_pago = request.POST.get('metodo_pago', 'tarjeta')
            logger.info(f"Iniciando proceso de pago - Método: {metodo_pago}, Tickets: {ticket_id_list}")

            # === PASO 6: GENERAR TRANSACTION ID ÚNICO ===
            transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            logger.info(f"Transaction ID generado: {transaction_id}")

            # === PASO 7: CREAR REGISTRO DE PAGO ===
            payment = Payment.objects.create(
                usuario=request.user,
                monto=total_amount,
                metodo_pago=metodo_pago,
                transaction_id=transaction_id,
                estado='procesando'
            )
            logger.info(f"Payment creado con ID: {payment.id}")

            # === PASO 8: ASOCIAR BOLETOS AL PAGO ===
            payment.boletos.set(tickets)
            logger.info(f"Boletos asociados al pago")

            # === PASO 9: SIMULAR PAYMENT INTENT ===
            simulated_payment_id = f"pi_{uuid.uuid4().hex[:16]}"
            try:
                payment.payment_intent_id = simulated_payment_id
                logger.info(f"Payment intent ID asignado")
            except Exception as e:
                logger.warning(f"No se pudo asignar payment_intent_id: {str(e)}")

            # === MARCAR PAGO COMO COMPLETADO ===
            payment.estado = 'completado'
            payment.save()
            logger.info(f"Payment marcado como completado")

            # === ACTUALIZAR ESTADO DE BOLETOS ===
            tickets.update(estado='pagado')
            logger.info(f"Tickets actualizados a estado 'pagado'")

            # === CREAR NOTIFICACIÓN ===
            try:
                from apps.users.models import Notification
                primera_rifa = tickets.first().rifa
                
                notif = Notification.objects.create(
                    usuario=request.user,
                    tipo='compra',
                    titulo='Compra de boletos exitosa',
                    mensaje=f'Has comprado {tickets.count()} boleto(s) para la rifa "{primera_rifa.titulo}". Total: CLP${total_amount:,.0f}',
                    enlace=f'/raffles/{primera_rifa.id}/',
                    rifa_relacionada=primera_rifa
                )
                logger.info(f"Notificación creada con ID: {notif.id}")
            except Exception as e:
                logger.error(f"Error creando notificación: {str(e)}", exc_info=True)
                # Continuar aunque falle la notificación

            # === MENSAJE FLASH Y REDIRECCIÓN ===
            messages.success(request, '¡Pago procesado exitosamente!')
            logger.info(f"Redirigiendo a payment_success con payment_id={payment.id}")
            return redirect('payments:payment_success', payment_id=payment.id)

        except Exception as e:
            logger.error(f"ERROR CRÍTICO en process_payment_view: {str(e)}", exc_info=True)
            messages.error(request, 'Error al procesar el pago. Por favor, contacta al soporte.')
            return redirect('raffles:raffle_list')

    # === PASO 11: RENDERIZAR FORMULARIO (GET) ===
    # Si el método no es POST, mostrar formulario de pago
    context = {
        'tickets': tickets,  # QuerySet de boletos a pagar
        'total_amount': total_amount,  # Monto total a cobrar
    }
    return render(request, 'payments/process.html', context)

# ============================================================================
# VISTA: payment_success_view
# ============================================================================
# Página de confirmación de pago exitoso
#
# URL: /payments/success/<payment_id>/
# Método: GET
# Autenticación: Requerida
#
# Muestra:
# - Detalles del pago (monto, método, fecha)
# - Lista de boletos comprados con números
# - Código QR de cada boleto (si aplica)
# - Link para descargar recibo
# - Próximos pasos
# ============================================================================
@login_required
def payment_success_view(request, payment_id):
    # Obtener pago o retornar 404
    # Filtro de seguridad: usuario=request.user
    # Solo el usuario propietario puede ver su pago
    payment = get_object_or_404(Payment, id=payment_id, usuario=request.user)

    # Renderizar template de éxito con contexto
    return render(request, 'payments/success.html', {'payment': payment})


# ============================================================================
# VISTA: payment_failed_view
# ============================================================================
# Página de error cuando el pago falla
#
# URL: /payments/failed/<payment_id>/
# Método: GET
# Autenticación: Requerida
#
# Muestra:
# - Mensaje de error detallado
# - Motivo del fallo (tarjeta declinada, fondos insuficientes, etc.)
# - Opciones para reintentar el pago
# - Link para contactar soporte si es error del sistema
# ============================================================================
@login_required
def payment_failed_view(request, payment_id):
    # Obtener pago fallido
    # Validación de seguridad con usuario=request.user
    payment = get_object_or_404(Payment, id=payment_id, usuario=request.user)

    # Renderizar template de fallo
    # El template puede mostrar detalles del error
    return render(request, 'payments/failed.html', {'payment': payment})
