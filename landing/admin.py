from django.contrib import admin
from .models import Especialidad, MedicoLanding, InformacionContacto

@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'activo']
    list_filter = ['tipo', 'activo']

@admin.register(MedicoLanding)
class MedicoLandingAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'especialidad', 'activo']

@admin.register(InformacionContacto)
class InformacionContactoAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Ubicación', {
            'fields': ('direccion',)
        }),
        ('Teléfonos', {
            'fields': ('telefono_1', 'telefono_2')
        }),
        ('Email', {
            'fields': ('email',)
        }),
        ('Horarios', {
            'fields': ('horario_lunes_viernes', 'horario_sabados', 'horario_domingos', 'emergencias_24h')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False