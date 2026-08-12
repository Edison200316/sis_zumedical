from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date, timedelta
import json
from .models import ControlPrenatal, HistoriaClinica

User = get_user_model()


class EditarControlPrenatalTest(TestCase):
    """Test suite para el endpoint de edición de controles prenatales (editar_control_prenatal)."""

    def setUp(self):
        """Configurar usuarios de prueba y controles prenatales."""
        self.client = Client()
        
        # Crear usuario médico
        self.medico = User.objects.create_user(
            username='medico_test',
            password='pass123456',
            email='medico@test.com',
            rol='medico'
        )
        
        # Crear usuario admin
        self.admin = User.objects.create_user(
            username='admin_test',
            password='pass123456',
            email='admin@test.com',
            rol='admin'
        )
        
        # Crear usuario paciente
        self.paciente = User.objects.create_user(
            username='paciente_test',
            password='pass123456',
            email='paciente@test.com',
            rol='paciente',
            genero='femenino'
        )
        perfil_paciente = self.paciente.paciente
        perfil_paciente.edad = 28
        perfil_paciente.medico_prenatal = self.medico
        perfil_paciente.estado_embarazo = 'ACTIVO'
        perfil_paciente.save()
        
        # Crear historia clínica para el paciente
        self.historia = HistoriaClinica.objects.create(
            paciente=self.paciente,
            medico=self.medico,
            peso_inicial=65.0,
            talla=1.62,
        )
        
        # Crear control prenatal de prueba
        self.control = ControlPrenatal.objects.create(
            paciente=self.paciente,
            medico=self.medico,
            semanas_gestacion=20,
            presion_arterial='120/80',
            peso=68.0,
            altura=1.62,
            glucosa=95.0,
            frecuencia_cardiaca=75,
            temperatura=98.6,
            embarazos_previos=1,
            diagnostico='Control prenatal normal',
            tratamiento='Vitaminas prenatales',
            observaciones='Todo normal',
            proxima_cita=date.today() + timedelta(weeks=4),
        )
        
        self.url = reverse('api_editar_control', kwargs={'control_id': self.control.id})

    def test_get_control_prenatal_authenticated_medico(self):
        """Test: GET devuelve datos del control para médico autenticado."""
        self.client.login(username='medico_test', password='pass123456')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], self.control.id)
        self.assertEqual(data['data']['semanas_gestacion'], 20)
        self.assertEqual(data['data']['presion_arterial'], '120/80')
        self.assertEqual(data['data']['peso'], 68.0)
        self.assertEqual(data['data']['glucosa'], 95.0)

    def test_get_control_prenatal_authenticated_admin(self):
        """Test: GET devuelve datos del control para admin autenticado."""
        self.client.login(username='admin_test', password='pass123456')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], self.control.id)

    def test_get_control_prenatal_no_authentication(self):
        """Test: GET rechaza acceso sin autenticación (redirect login)."""
        response = self.client.get(self.url)
        # Django redirige a login cuando no está autenticado
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login') or response.url.startswith('/login'))

    def test_get_control_prenatal_paciente_access_denied(self):
        """Test: GET rechaza acceso a paciente (no médico/admin)."""
        self.client.login(username='paciente_test', password='pass123456')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('permisos', data['error'].lower())

    def test_post_edit_control_valid_data_medico(self):
        """Test: POST actualiza control con datos válidos (médico)."""
        self.client.login(username='medico_test', password='pass123456')
        
        updated_data = {
            'paciente': self.paciente.id,
            'semanas_gestacion': 24,
            'presion_arterial': '118/78',
            'peso': 70.0,
            'altura': 1.62,
            'glucosa': 98.0,
            'frecuencia_cardiaca': 72,
            'temperatura': 98.4,
            'embarazos_previos': 1,
            'diagnostico': 'Control prenatal normal - 24 semanas',
            'tratamiento': 'Vitaminas prenatales + calcio',
            'observaciones': 'Presión estable',
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verificar que el control se actualizó en la BD
        self.control.refresh_from_db()
        self.assertEqual(self.control.semanas_gestacion, 24)
        self.assertEqual(self.control.presion_arterial, '118/78')
        self.assertEqual(self.control.peso, 70.0)
        self.assertEqual(self.control.glucosa, 98.0)

    def test_post_edit_control_valid_data_admin(self):
        """Test: POST actualiza control con datos válidos (admin)."""
        self.client.login(username='admin_test', password='pass123456')
        
        updated_data = {
            'paciente': self.paciente.id,
            'semanas_gestacion': 28,
            'presion_arterial': '122/82',
            'peso': 72.0,
            'altura': 1.62,
            'glucosa': 100.0,
            'frecuencia_cardiaca': 76,
            'temperatura': 98.5,
            'embarazos_previos': 1,
            'diagnostico': 'Control prenatal - 28 semanas',
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        self.control.refresh_from_db()
        self.assertEqual(self.control.semanas_gestacion, 28)

    def test_post_edit_control_paciente_access_denied(self):
        """Test: POST rechaza acceso a paciente (no médico/admin)."""
        self.client.login(username='paciente_test', password='pass123456')
        
        updated_data = {
            'semanas_gestacion': 30,
            'presion_arterial': '120/80',
            'peso': 75.0,
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_post_edit_control_invalid_json(self):
        """Test: POST rechaza JSON inválido."""
        self.client.login(username='medico_test', password='pass123456')
        
        response = self.client.post(
            self.url,
            data='{"invalid json}',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('inválidos', data['error'].lower())

    def test_post_edit_control_rechaza_campo_ia_en_cero(self):
        """Test: POST rechaza datos clínicos irreales para la IA."""
        self.client.login(username='medico_test', password='pass123456')
        
        updated_data = {
            'paciente': self.paciente.id,
            'semanas_gestacion': 0,
            'presion_arterial': '120/80',
            'peso': 70.0,
            'altura': 1.62,
            'glucosa': 95.0,
            'frecuencia_cardiaca': 75,
            'temperatura': 98.6,
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('error', data.keys())
        self.assertIn('errors', data.keys())

    def test_post_edit_control_invalid_semanas_gestacion(self):
        """Test: POST rechaza valor inválido para semanas_gestacion."""
        self.client.login(username='medico_test', password='pass123456')
        
        updated_data = {
            'paciente': self.paciente.id,
            'semanas_gestacion': 'invalid',  # No es número
            'presion_arterial': '120/80',
            'peso': 70.0,
            'altura': 1.62,
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_post_edit_control_invalid_peso(self):
        """Test: POST rechaza valor inválido para peso."""
        self.client.login(username='medico_test', password='pass123456')
        
        updated_data = {
            'paciente': self.paciente.id,
            'semanas_gestacion': 24,
            'presion_arterial': '120/80',
            'peso': 'invalid',  # No es número
            'altura': 1.62,
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_post_edit_control_nonexistent_control(self):
        """Test: GET/POST retorna 404 para control inexistente."""
        self.client.login(username='medico_test', password='pass123456')
        
        fake_url = reverse('api_editar_control', kwargs={'control_id': 9999})
        response = self.client.get(fake_url)
        
        self.assertEqual(response.status_code, 404)

    def test_post_edit_control_partial_update(self):
        """Test: POST puede actualizar solo algunos campos."""
        self.client.login(username='medico_test', password='pass123456')
        
        original_diagnostico = self.control.diagnostico
        
        updated_data = {
            'paciente': self.paciente.id,
            'semanas_gestacion': 20,
            'presion_arterial': '115/75',  # Solo cambiar presión
            'peso': 68.0,
            'altura': 1.62,
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.control.refresh_from_db()
        self.assertEqual(self.control.presion_arterial, '115/75')
        # El diagnóstico original debe mantenerse si no se modifica
        self.assertEqual(self.control.diagnostico, original_diagnostico)

    def test_post_edit_control_preserves_creation_date(self):
        """Test: Editar control no cambia la fecha de creación."""
        self.client.login(username='medico_test', password='pass123456')
        
        original_fecha = self.control.fecha
        
        updated_data = {
            'paciente': self.paciente.id,
            'semanas_gestacion': 24,
            'presion_arterial': '120/80',
            'peso': 70.0,
            'altura': 1.62,
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.control.refresh_from_db()
        # Verificar que la fecha no cambió
        self.assertEqual(self.control.fecha, original_fecha)

    def test_get_control_returns_all_fields(self):
        """Test: GET retorna todos los campos del control."""
        self.client.login(username='medico_test', password='pass123456')
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Verificar que contiene todos los campos importantes
        required_fields = [
            'id', 'fecha', 'semanas_gestacion', 'presion_arterial',
            'glucosa', 'peso', 'altura', 'frecuencia_cardiaca',
            'temperatura', 'diagnostico', 'tratamiento', 'observaciones',
            'proxima_cita', 'examen_fisico', 'resultado_examenes',
            'evolucion', 'proteinuria'
        ]
        
        for field in required_fields:
            self.assertIn(field, data['data'])

    def test_post_edit_control_with_empty_optional_fields(self):
        """Test: POST puede dejar campos opcionales vacíos."""
        self.client.login(username='medico_test', password='pass123456')
        
        updated_data = {
            'paciente': self.paciente.id,
            'semanas_gestacion': 24,
            'presion_arterial': '120/80',
            'peso': 70.0,
            'altura': 1.62,
            'diagnostico': '',  # Campo opcional, dejarlo vacío
            'tratamiento': '',  # Campo opcional, dejarlo vacío
            'observaciones': '',  # Campo opcional, dejarlo vacío
        }
        
        response = self.client.post(
            self.url,
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase

from pacientes.models import Paciente
from control_prenatal.forms import ControlPrenatalForm as ControlPrenatalAppForm
from usuarios.forms import ControlPrenatalForm as MedicoControlPrenatalForm


class ControlPrenatalFormValidacionIATest(TestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT setval(
                    pg_get_serial_sequence('pacientes_paciente', 'id'),
                    COALESCE((SELECT MAX(id) FROM pacientes_paciente), 1),
                    true
                )
                """
            )
        User = get_user_model()
        self.medico = User.objects.create_user(
            username='medico_ia_validacion',
            password='Aa1!aaaa',
            first_name='Medico',
            last_name='IA',
            rol='medico',
        )
        self.paciente_user = User.objects.create_user(
            username='paciente_ia_validacion',
            password='Aa1!aaaa',
            first_name='Paciente',
            last_name='IA',
            rol='paciente',
        )
        paciente = self.paciente_user.paciente
        paciente.cedula = '1234567890'
        paciente.edad = 28
        paciente.medico_prenatal = self.medico
        paciente.estado_embarazo = 'ACTIVO'
        paciente.save()

    def datos_validos(self):
        return {
            'paciente': self.paciente_user.id,
            'semanas_gestacion': 24,
            'presion_arterial': '120/80',
            'peso': 68.5,
            'altura': 1.62,
            'glucosa': 92,
            'frecuencia_cardiaca': 76,
            'temperatura': 98.6,
            'embarazos_previos': 0,
            'proteinuria': 'Negativa',
            'observaciones': 'Control normal',
        }

    def assert_formulario_rechaza(self, form_class, campo, valor):
        data = self.datos_validos()
        data[campo] = valor
        form = form_class(data, medico=self.medico)
        self.assertFalse(form.is_valid())
        self.assertIn(campo, form.errors)

    def test_formularios_aceptan_datos_clinicos_reales(self):
        for form_class in (ControlPrenatalAppForm, MedicoControlPrenatalForm):
            form = form_class(self.datos_validos(), medico=self.medico)
            self.assertTrue(form.is_valid(), form.errors)

    def test_formularios_rechazan_ceros_en_campos_ia(self):
        campos = [
            'semanas_gestacion',
            'peso',
            'altura',
            'glucosa',
            'frecuencia_cardiaca',
            'temperatura',
        ]
        for form_class in (ControlPrenatalAppForm, MedicoControlPrenatalForm):
            for campo in campos:
                with self.subTest(form=form_class.__module__, campo=campo):
                    self.assert_formulario_rechaza(form_class, campo, 0)

    def test_formularios_rechazan_presion_irreal(self):
        for form_class in (ControlPrenatalAppForm, MedicoControlPrenatalForm):
            with self.subTest(form=form_class.__module__):
                self.assert_formulario_rechaza(form_class, 'presion_arterial', '0/0')
                self.assert_formulario_rechaza(form_class, 'presion_arterial', '80/120')
