"""
Formularios de Django para validación de datos de entrada.
CORREGIDO: El método save() ahora usa update_or_create() para
no chocar con la señal que crea el perfil automáticamente.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Perfil, Departamento, Documento, Equipo, Componente, Ticket, MensajeTicket
from .models import CursoCapacitacion, EvaluacionCurso, PoliticaSeguridad, RegistroIncidente


class FormularioLogin(AuthenticationForm):
    """Formulario personalizado para el login."""
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Ingrese su nombre de usuario',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': 'Ingrese su contraseña',
            'autocomplete': 'current-password',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages['invalid_login'] = (
            'Nombre de usuario o contraseña incorrectos.'
        )


class FormularioRegistro(forms.ModelForm):
    """Formulario para registrar nuevos usuarios."""
    
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input-field password-input',
            'placeholder': 'Mínimo 8 caracteres',
            'id': 'password1',
        }),
        min_length=8,
    )
    
    password_confirmar = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input-field password-input',
            'placeholder': 'Repita la contraseña',
            'id': 'password2',
        }),
        min_length=8,
    )
    
    nombre_completo = forms.CharField(
        label='Nombre completo',
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Ej: Juan Pérez García',
        }),
        max_length=200,
    )
    
    cargo = forms.CharField(
        label='Cargo',
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': 'Ej: Especialista en Redes',
        }),
        max_length=150,
    )
    
    departamento = forms.ModelChoiceField(
        label='Departamento',
        queryset=Departamento.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': 'input-field'}),
        empty_label='Seleccione un departamento',
    )

    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Nombre de usuario para iniciar sesión',
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya existe.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Mínimo 8 caracteres.')
        if not any(c.isupper() for c in password):
            raise forms.ValidationError('Debe incluir una mayúscula.')
        if not any(c.islower() for c in password):
            raise forms.ValidationError('Debe incluir una minúscula.')
        if not any(c.isdigit() for c in password):
            raise forms.ValidationError('Debe incluir un número.')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            raise forms.ValidationError('Debe incluir un carácter especial.')
        return password

    def clean_password_confirmar(self):
        password = self.cleaned_data.get('password')
        confirmar = self.cleaned_data.get('password_confirmar')
        if password and confirmar and password != confirmar:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return confirmar

    def save(self, commit=True):
        """
        Guarda el usuario con contraseña encriptada.
        CORREGIDO: Usa update_or_create() en vez de create() porque
        la señal (signals.py) ya crea un perfil vacío cuando se guarda
        el usuario. Aquí solo ACTUALIZAMOS ese perfil con los datos
        del formulario. Esto evita el error UNIQUE constraint.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            # ACTUALIZAR el perfil que la señal ya creó (no crear nuevo)
            Perfil.objects.update_or_create(
                user=user,
                defaults={
                    'nombre_completo': self.cleaned_data['nombre_completo'],
                    'cargo': self.cleaned_data['cargo'],
                    'departamento': self.cleaned_data['departamento'],
                    'rol': 'usuario',
                }
            )
        
        return user


class FormularioDocumento(forms.ModelForm):
    """Formulario para subir documentos."""
    class Meta:
        model = Documento
        fields = ['archivo', 'descripcion', 'visible_todos', 'departamentos_visibles']
        widgets = {
            'archivo': forms.FileInput(attrs={
                'class': 'input-field',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.rar,.txt,.jpg,.png'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'input-field', 'rows': 3,
                'placeholder': 'Descripción del documento...',
            }),
            'visible_todos': forms.CheckboxInput(attrs={
                'class': 'checkbox-custom', 'id': 'visible_todos_check',
            }),
            'departamentos_visibles': forms.CheckboxSelectMultiple(attrs={
                'class': 'checkbox-group',
            }),
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo and archivo.size > 50 * 1024 * 1024:
            raise forms.ValidationError('Máximo 50 MB.')
        return archivo


class FormularioEquipo(forms.ModelForm):
    """Formulario para registrar/editar equipos."""
    class Meta:
        model = Equipo
        fields = [
            'identificacion', 'tipo_equipo', 'marca', 'modelo', 'estado',
            'ubicacion', 'departamento', 'ip', 'mac', 'sistema_operativo',
            'numero_inventario', 'responsable', 'observaciones'
        ]
        widgets = {
            'identificacion': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'PC-001'}),
            'tipo_equipo': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Desktop, Laptop...'}),
            'marca': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Lenovo, HP...'}),
            'modelo': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'ThinkPad T480...'}),
            'estado': forms.Select(attrs={'class': 'input-field'}),
            'ubicacion': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Oficina 201'}),
            'departamento': forms.Select(attrs={'class': 'input-field'}),
            'ip': forms.TextInput(attrs={'class': 'input-field', 'placeholder': '192.168.1.100'}),
            'mac': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'AA:BB:CC:DD:EE:FF'}),
            'sistema_operativo': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Windows 11...'}),
            'numero_inventario': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'INV-2024-0001'}),
            'responsable': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Nombre del responsable'}),
            'observaciones': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
        }

    def clean_mac(self):
        mac = self.cleaned_data.get('mac', '').strip()
        if mac:
            import re
            if not re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', mac):
                raise forms.ValidationError('Formato: AA:BB:CC:DD:EE:FF')
        return mac


class FormularioComponente(forms.ModelForm):
    """Formulario para agregar/editar componentes."""
    class Meta:
        model = Componente
        fields = ['tipo', 'marca', 'modelo', 'especificaciones', 
                  'numero_serie', 'capacidad', 'estado']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'input-field'}),
            'marca': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Intel, Samsung...'}),
            'modelo': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Core i5-10400...'}),
            'especificaciones': forms.Textarea(attrs={'class': 'input-field', 'rows': 2}),
            'numero_serie': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Número de serie'}),
            'capacidad': forms.TextInput(attrs={'class': 'input-field', 'placeholder': '8GB, 500GB...'}),
            'estado': forms.Select(attrs={'class': 'input-field'}),
        }

# ══════════════════════════════════════════════════════════════
# FORMULARIOS DE SEGURIDAD AVANZADA
# ══════════════════════════════════════════════════════════════

from django.core.exceptions import ValidationError


class FormularioVerificar2FA(forms.Form):
    """Formulario para ingresar el código TOTP de 6 dígitos."""
    codigo = forms.CharField(
        label='Código de verificación',
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': '000000',
            'maxlength': 6,
            'style': 'font-size:2rem; text-align:center; letter-spacing:8px; font-family: var(--font-mono);',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
        }),
        min_length=6,
        max_length=6,
    )

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo', '')
        if not codigo.isdigit():
            raise ValidationError('Solo se permiten números.')
        if len(codigo) != 6:
            raise ValidationError('El código debe tener exactamente 6 dígitos.')
        return codigo


class FormularioCambiarPassword(forms.Form):
    """Formulario para cambiar la contraseña (forzado o voluntario)."""
    password_actual = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Su contraseña actual'}),
    )
    password_nueva = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input-field password-input', 'placeholder': 'Mínimo 8 caracteres', 'id': 'pwd_nueva'
        }),
        min_length=8,
    )
    password_confirmar = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input-field password-input', 'placeholder': 'Repita la nueva', 'id': 'pwd_confirmar'
        }),
        min_length=8,
    )

    def clean_password_nueva(self):
        p = self.cleaned_data.get('password_nueva')
        if p:
            if len(p) < 8: raise ValidationError('Mínimo 8 caracteres.')
            if not any(c.isupper() for c in p): raise ValidationError('Falta mayúscula.')
            if not any(c.islower() for c in p): raise ValidationError('Falta minúscula.')
            if not any(c.isdigit() for c in p): raise ValidationError('Falta número.')
            if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in p): raise ValidationError('Falta carácter especial.')
        return p

    def clean_password_confirmar(self):
        n = self.cleaned_data.get('password_nueva')
        c = self.cleaned_data.get('password_confirmar')
        if n and c and n != c:
            raise ValidationError('Las contraseñas no coinciden.')
        return c
    
class FormularioTicket(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['titulo', 'descripcion', 'prioridad']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'input-field'}),
            'descripcion': forms.Textarea(attrs={'class': 'input-field', 'rows': 4}),
            'prioridad': forms.Select(attrs={'class': 'input-field'})
        }

class FormularioMensajeTicket(forms.Form):
    contenido = forms.CharField(widget=forms.Textarea(attrs={'class': 'input-field', 'rows': 3, 'placeholder': 'Escriba su respuesta...'}))

from .models import CursoCapacitacion, EvaluacionCurso, PoliticaSeguridad

class FormularioCurso(forms.ModelForm):
    class Meta:
        model = CursoCapacitacion
        fields = ['titulo', 'descripcion', 'preguntas']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'input-field'}),
            'descripcion': forms.Textarea(attrs={'class': 'input-field', 'rows': 3}),
            'preguntas': forms.Textarea(attrs={'class': 'input-field', 'rows': 10, 'placeholder': '[{"p": "¿Pregunta?", "o": ["Opción 1", "Opción 2", "Opción 3", "Opción 4"], "r": 0}]'})
        }

class FormularioPolitica(forms.ModelForm):
    class Meta:
        model = PoliticaSeguridad
        fields = ['nombre', 'contenido', 'fecha_vigencia']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input-field'}),
            'contenido': forms.Textarea(attrs={'class': 'input-field', 'rows': 8}),
            'fecha_vigencia': forms.DateInput(attrs={'class': 'input-field', 'type': 'date'})
        }

class FormularioDepartamento(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['nombre', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Ej: Dirección de Informática'}),
            'activo': forms.CheckboxInput(attrs={'class': 'checkbox-label', 'style': 'width: auto; accent-color: var(--accent-cyan);'})
        }

class FormularioIncidente(forms.ModelForm):
    class Meta:
        model = RegistroIncidente
        fields = ['tipo_incidente', 'descripcion', 'estado']
        widgets = {
            'tipo_incidente': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Ej: Infección por Malware, Phishing, Fuga de datos...'}),
            'descripcion': forms.Textarea(attrs={'class': 'input-field', 'rows': 6}),
            'estado': forms.Select(attrs={'class': 'input-field'})
        }