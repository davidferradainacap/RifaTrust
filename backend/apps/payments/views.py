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
import stripe
# - SDK de Stripe para procesamiento de pagos
# - Documentación: https://stripe.com/docs/api

import uuid
# - Generador de identificadores únicos universales (UUID4)
# - Usado para transaction_id únicos

# === CONFIGURACIÓN DE STRIPE ===
stripe.api_key = settings.STRIPE_SECRET_KEY
# - Clave secreta de Stripe desde settings.py
# - NUNCA exponer en frontend o commits de Git
# - Formato: sk_test_... (test) o sk_live_... (producción)

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
        # Obtener método de pago seleccionado por usuario
        # Opciones: stripe (default), paypal, tarjeta, transferencia
        metodo_pago = request.POST.get('metodo_pago', 'stripe')

        # === PASO 6: GENERAR TRANSACTION ID ÚNICO ===
        # Formato: TXN-{12 caracteres hexadecimales en mayúsculas}
        # Ejemplo: TXN-A3F5E9B2C4D7
        # UUID4 genera un identificador único aleatorio
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

        # === PASO 7: CREAR REGISTRO DE PAGO ===
        # Estado inicial: 'procesando' (ni completado ni fallido aún)
        payment = Payment.objects.create(
            usuario=request.user,
            monto=total_amount,
            metodo_pago=metodo_pago,
            transaction_id=transaction_id,  # ID único encriptado
            estado='procesando'  # Estado transitorio
        )

        # === PASO 8: ASOCIAR BOLETOS AL PAGO ===
        # ManyToMany: Un pago puede tener múltiples boletos
        # set() reemplaza todas las relaciones existentes
        payment.boletos.set(tickets)

        # === PASO 9: PROCESAR PAGO CON STRIPE ===
        if metodo_pago == 'stripe':
            try:
                # === PASO 9.1: CREAR PAYMENT INTENT EN STRIPE ===
                # Payment Intent: objeto de Stripe que rastrea el pago
                intent = stripe.PaymentIntent.create(
                    # Stripe requiere montos en centavos (menor denominación)
                    # $150.00 = 15000 centavos
                    amount=int(total_amount * 100),

                    # Moneda en formato ISO 4217
                    # 'mxn' = Peso Mexicano
                    # 'clp' = Peso Chileno
                    # 'usd' = Dólar Americano
                    currency='mxn',

                    # Metadata: información adicional para rastreo
                    # Visible en el dashboard de Stripe
                    metadata={
                        'transaction_id': transaction_id,
                        'user_id': request.user.id
                    }
                )

                # === PASO 9.2: GUARDAR PAYMENT INTENT ID ===
                # Campo encriptado (EncryptedCharField)
                # Ejemplo: pi_1A2B3C4D5E6F7G8H
                payment.payment_intent_id = intent.id

                # === PASO 9.3: MARCAR PAGO COMO COMPLETADO ===
                payment.estado = 'completado'
                payment.save()

                # === PASO 9.4: ACTUALIZAR ESTADO DE BOLETOS ===
                # De 'reservado' a 'pagado'
                # update() es más eficiente que iterar y guardar uno por uno
                tickets.update(estado='pagado')

                # === PASO 9.5: CREAR NOTIFICACIÓN DE COMPRA EXITOSA ===
                from apps.users.models import Notification
                primera_rifa = tickets.first().rifa  # Obtener rifa del primer boleto

                Notification.objects.create(
                    usuario=request.user,
                    tipo='compra',  # Tipo de notificación
                    titulo='Compra de boletos exitosa',
                    mensaje=f'Has comprado {tickets.count()} boleto(s) para la rifa "{primera_rifa.titulo}". Total: ${total_amount}',
                    enlace=f'/raffles/{primera_rifa.id}/',  # Link al detalle de la rifa
                    rifa_relacionada=primera_rifa
                )

                # === PASO 9.6: MENSAJE FLASH Y REDIRECCIÓN ===
                messages.success(request, '¡Pago procesado exitosamente!')
                return redirect('payments:payment_success', payment_id=payment.id)

            # === PASO 9.7: MANEJO DE ERRORES DE STRIPE ===
            except stripe.error.StripeError as e:
                # Errores comunes:
                # - CardError: Tarjeta declinada o sin fondos
                # - InvalidRequestError: Parámetros inválidos
                # - AuthenticationError: Clave API incorrecta
                # - APIConnectionError: Sin conexión a Stripe
                payment.estado = 'fallido'
                payment.save()

                error_msg = handle_exception_safely(e, 'payment', 'Procesamiento de pago con Stripe')
                messages.error(request, error_msg)
                return redirect('payments:payment_failed', payment_id=payment.id)

        # === PASO 10: OTROS MÉTODOS DE PAGO ===
        else:
            # PayPal, transferencia, efectivo, etc.
            # NOTA: En este momento está simulado
            # TODO: Implementar integración con PayPal SDK
            # TODO: Implementar verificación de transferencias bancarias

            payment.estado = 'completado'
            payment.save()

            # Actualizar boletos a pagados
            tickets.update(estado='pagado')

            # === CREAR NOTIFICACIÓN ===
            from apps.users.models import Notification
            primera_rifa = tickets.first().rifa
            Notification.objects.create(
                usuario=request.user,
                tipo='compra',
                titulo='Compra de boletos exitosa',
                mensaje=f'Has comprado {tickets.count()} boleto(s) para la rifa "{primera_rifa.titulo}". Total: ${total_amount}',
                enlace=f'/raffles/{primera_rifa.id}/',
                rifa_relacionada=primera_rifa
            )

            messages.success(request, '¡Pago procesado exitosamente!')
            return redirect('payments:payment_success', payment_id=payment.id)

    # === PASO 11: RENDERIZAR FORMULARIO (GET) ===
    # Si el método no es POST, mostrar formulario de pago
    context = {
        'tickets': tickets,  # QuerySet de boletos a pagar
        'total_amount': total_amount,  # Monto total a cobrar
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,  # Clave pública para frontend
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
