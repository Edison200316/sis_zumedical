from django.test import TestCase, Client
from django.urls import reverse

from pacientes.models import Paciente
from usuarios.models import Usuario


class ProgramarPartoViewTest(TestCase):
    def test_programar_parto_page_renders_for_medico(self):
        medico = Usuario.objects.create_user(
            username='medico_test',
            password='testpass123',
            rol='medico',
        )
        paciente = Usuario.objects.create_user(
            username='paciente_test',
            password='testpass123',
            rol='paciente',
        )
        Paciente.objects.create(
            usuario=paciente,
            estado_embarazo='ACTIVO',
            medico_prenatal=medico,
        )

        client = Client()
        client.force_login(medico)

        response = client.get(reverse('programar_parto'))

        self.assertEqual(response.status_code, 200)
