from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='paciente_general_dashboard'),
    path('mis-citas/', views.mis_citas, name='paciente_general_citas'),
    path('agendar/', views.agendar_cita, name='paciente_general_agendar'),
    path('cancelar/<int:cita_id>/', views.cancelar_cita, name='paciente_general_cancelar'),
    path('mi-perfil/', views.mi_perfil, name='paciente_general_perfil'),
    path('medicos-disponibles/', views.medicos_disponibles, name='paciente_general_medicos'),
    path('horas-disponibles/', views.horas_disponibles, name='paciente_general_horas'),
    path('mis-consultas/', views.mis_consultas, name='paciente_general_consultas'),
    path('consulta/<int:consulta_id>/', views.ver_consulta, name='paciente_general_ver_consulta'),
    path('consulta/<int:consulta_id>/descargar-pdf/', views.descargar_consulta_pdf, name='paciente_general_descargar_consulta'),
]