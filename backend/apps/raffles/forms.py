from django import forms
from .models import Raffle, SponsorshipRequest, OrganizerSponsorRequest

class RaffleForm(forms.ModelForm):
    class Meta:
        model = Raffle
        fields = [
            'titulo', 'descripcion', 'imagen', 'precio_boleto', 'total_boletos',
            'fecha_sorteo', 'premio_principal', 'descripcion_premio', 'imagen_premio', 'valor_premio',
            'documento_legal', 'estado', 'permite_multiples_boletos', 'max_boletos_por_usuario'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la rifa'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe tu rifa...'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
            'precio_boleto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'total_boletos': forms.NumberInput(attrs={'class': 'form-control', 'min': '100', 'placeholder': 'Mínimo 100 boletos'}),
            'fecha_sorteo': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'premio_principal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: iPhone 15 Pro'}),
            'descripcion_premio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen_premio': forms.FileInput(attrs={'class': 'form-control'}),
            'valor_premio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Ej: 500000'}),
            'documento_legal': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'permite_multiples_boletos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_boletos_por_usuario': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limitar opciones de estado para organizadores
        # Si la rifa está aprobada, permitir activarla
        if self.instance.pk and self.instance.estado == 'aprobada':
            self.fields['estado'].choices = [
                ('aprobada', 'Aprobada (en espera)'),
                ('activa', 'Activar Rifa'),
            ]
        else:
            self.fields['estado'].choices = [
                ('borrador', 'Borrador'),
                ('pendiente_aprobacion', 'Solicitar Aprobación'),
            ]
        
        # Hacer todos los campos obligatorios
        self.fields['titulo'].required = True
        self.fields['descripcion'].required = True
        self.fields['imagen'].required = True
        self.fields['precio_boleto'].required = True
        self.fields['total_boletos'].required = True
        self.fields['fecha_sorteo'].required = True
        self.fields['premio_principal'].required = True
        self.fields['descripcion_premio'].required = True
        self.fields['imagen_premio'].required = True
        self.fields['valor_premio'].required = True
        self.fields['documento_legal'].required = True
        self.fields['estado'].required = True
        self.fields['permite_multiples_boletos'].required = True
        self.fields['max_boletos_por_usuario'].required = True
        
        # Si es una nueva rifa, establecer 'borrador' como valor por defecto
        if not self.instance.pk:
            self.fields['estado'].initial = 'borrador'
    
    def clean_estado(self):
        estado = self.cleaned_data.get('estado')
        
        # Si la rifa está aprobada, permitir activarla
        if self.instance.pk and self.instance.estado == 'aprobada':
            if estado not in ['aprobada', 'activa']:
                raise forms.ValidationError('Solo puedes mantener "Aprobada" o cambiar a "Activa"')
        else:
            if estado not in ['borrador', 'pendiente_aprobacion']:
                raise forms.ValidationError('Debes seleccionar "Borrador" o "Solicitar Aprobación"')
        
        return estado
    
    def clean_documento_legal(self):
        documento = self.cleaned_data.get('documento_legal')
        
        if documento:
            # Validar tamaño del archivo (máximo 10MB)
            if documento.size > 10 * 1024 * 1024:
                raise forms.ValidationError('El documento no puede superar los 10MB')
            
            # Validar tipo de archivo
            extensiones_permitidas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            nombre_archivo = documento.name.lower()
            if not any(nombre_archivo.endswith(ext) for ext in extensiones_permitidas):
                raise forms.ValidationError('Solo se permiten archivos PDF, Word o imágenes (JPG, PNG)')
        
        return documento
    
    def clean(self):
        cleaned_data = super().clean()
        valor_premio = cleaned_data.get('valor_premio')
        precio_boleto = cleaned_data.get('precio_boleto')
        total_boletos = cleaned_data.get('total_boletos')
        
        # Validar mínimo de 100 boletos
        if total_boletos and total_boletos < 100:
            raise forms.ValidationError(
                f'⚠️ El número mínimo de boletos es 100. Actualmente tienes {total_boletos} boletos configurados.'
            )
        
        # Validar rentabilidad solo si todos los campos necesarios están presentes
        if valor_premio and precio_boleto and total_boletos:
            # Calcular el ingreso total si se venden todos los boletos
            ingreso_total = precio_boleto * total_boletos
            
            # El ingreso total debe ser al menos el doble del valor del premio
            minimo_requerido = valor_premio * 2
            
            if ingreso_total < minimo_requerido:
                # Calcular cuántos boletos mínimos se necesitan
                boletos_minimos = max(100, int((minimo_requerido / precio_boleto) + 1))
                
                raise forms.ValidationError(
                    f'⚠️ El ingreso total (${precio_boleto:,.0f} × {total_boletos:,} = ${ingreso_total:,.0f}) '
                    f'debe ser al menos el doble del valor del premio (${valor_premio:,.0f} × 2 = ${minimo_requerido:,.0f}). '
                    f'Necesitas vender al menos {boletos_minimos:,} boletos a ${precio_boleto:,.0f} cada uno, '
                    f'o aumentar el precio del boleto.'
                )
        
        return cleaned_data


class SponsorshipRequestForm(forms.ModelForm):
    """Formulario para que un sponsor envíe solicitud de patrocinio"""
    
    class Meta:
        model = SponsorshipRequest
        fields = [
            'nombre_premio_adicional', 'descripcion_premio', 'valor_premio', 
            'imagen_premio', 'nombre_marca', 'logo_marca', 'sitio_web', 
            'mensaje_patrocinio'
        ]
        widgets = {
            'nombre_premio_adicional': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Kit Premium de Productos'
            }),
            'descripcion_premio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el premio adicional que aportarás...'
            }),
            'valor_premio': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '1',
                'placeholder': 'Valor en CLP'
            }),
            'imagen_premio': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'nombre_marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de tu marca o empresa'
            }),
            'logo_marca': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'sitio_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://tumarca.com'
            }),
            'mensaje_patrocinio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Mensaje para el organizador explicando por qué quieres patrocinar esta rifa...'
            }),
        }


class OrganizerSponsorInvitationForm(forms.ModelForm):
    """Formulario para que un organizador invite a un sponsor"""
    
    class Meta:
        model = OrganizerSponsorRequest
        fields = ['rifa', 'mensaje_invitacion', 'beneficios_ofrecidos']
        widgets = {
            'rifa': forms.Select(attrs={
                'class': 'form-control'
            }),
            'mensaje_invitacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escribe un mensaje personalizado para el sponsor...'
            }),
            'beneficios_ofrecidos': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe qué beneficios recibirá el sponsor (visibilidad, exposición de marca, etc.)...'
            }),
        }
    
    def __init__(self, *args, organizador=None, **kwargs):
        super().__init__(*args, **kwargs)
        if organizador:
            # Solo mostrar rifas activas del organizador
            self.fields['rifa'].queryset = Raffle.objects.filter(
                organizador=organizador,
                estado='activa'
            )
