# ============================================================================
# MÓDULO DE FORMULARIOS - USERS
# ============================================================================
# Formularios para registro, autenticación y perfil de usuarios
# Incluye validaciones personalizadas y widgets con estilos Bootstrap
# ============================================================================

# === IMPORTACIONES DJANGO FORMS ===
from django import forms
# - forms: Módulo base para formularios Django

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# - UserCreationForm: Formulario base para registro de usuarios
# - AuthenticationForm: Formulario base para login

# === IMPORTACIONES DE MODELOS ===
from .models import User, Profile
# - User: Modelo personalizado de usuario
# - Profile: Perfil extendido del usuario

# === IMPORTACIONES PYTHON ===
from datetime import date, timedelta
# - date: Manipulación de fechas
# - timedelta: Cálculo de diferencias de fechas (para validar edad)

# === IMPORTACIONES PARA VALIDACIÓN DE EMAIL ===
from apps.core.email_validator import verify_email
# - verify_email: Función para validar emails con AbstractAPI
import logging
# - logging: Para registrar advertencias y errores
logger = logging.getLogger(__name__)

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'autocomplete': 'email'
        })
    )
    nombre = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre completo',
            'autocomplete': 'name'
        })
    )
    fecha_nacimiento = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'max': (date.today() - timedelta(days=365*18)).isoformat()
        }),
        help_text='Debes ser mayor de 18 años para registrarte'
    )
    telefono = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56 9 1234 5678',
            'autocomplete': 'tel'
        }),
        help_text='Formato: +56 9 1234 5678'
    )
    rol = forms.ChoiceField(
        choices=[
            ('participante', 'Participante'),
            ('organizador', 'Organizador'),
            ('sponsor', 'Sponsor')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
            'autocomplete': 'new-password'
        })
    )
    aceptar_terminos = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        error_messages={
            'required': 'Debes aceptar los términos y condiciones para registrarte'
        },
        help_text='He leído y acepto los términos y condiciones'
    )

    class Meta:
        model = User
        fields = ['email', 'nombre', 'fecha_nacimiento', 'telefono', 'rol', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Verificar si el email ya está registrado
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado')

        # Verificar validez del email con API externa
        try:
            verification_result = verify_email(email)

            # Verificar si el email es desechable
            if verification_result.get('is_disposable', False):
                logger.warning(f"Intento de registro con email desechable: {email}")
                raise forms.ValidationError(
                    'No se permiten correos temporales o desechables. '
                    'Por favor usa un correo válido.'
                )

            # Verificar si el email es válido (formato y dominio)
            if not verification_result.get('is_valid', False):
                logger.warning(f"Intento de registro con email inválido: {email}")
                raise forms.ValidationError(
                    'El correo electrónico no es válido o no existe. '
                    'Por favor verifica e intenta nuevamente.'
                )

            # Verificar calidad del email (score)
            quality_score = verification_result.get('quality_score', 0.0)
            if quality_score < 0.5:
                logger.warning(f"Email con baja calidad detectado: {email} (score: {quality_score})")
                raise forms.ValidationError(
                    'El correo electrónico parece tener problemas. '
                    'Por favor usa otro correo o contacta al soporte.'
                )

            logger.info(f"Email verificado exitosamente: {email} (score: {quality_score})")

        except forms.ValidationError:
            # Re-lanzar errores de validación
            raise
        except Exception as e:
            # Si la API falla, solo registrar el error pero permitir el registro
            logger.error(f"Error al verificar email {email}: {str(e)}")
            # No bloquear el registro si la API falla

        return email

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            today = date.today()
            age = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if age < 18:
                raise forms.ValidationError('Debes ser mayor de edad (18 años) para registrarte')
        return fecha_nacimiento

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'autocomplete': 'email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password'
        })
    )


class ProfileForm(forms.ModelForm):
    telefono = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56 9 1234 5678'
        })
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = Profile
        fields = ['direccion', 'ciudad', 'estado', 'codigo_postal', 'pais']
        widgets = {
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
        }
