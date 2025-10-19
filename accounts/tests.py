from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import DoctorAssignmentLog

User = get_user_model()

class DoctorCodeTestCase(TestCase):
    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor1',
            email='doctor@example.com',
            password='pass123',
            user_type='doctor',
            first_name='John',
            last_name='Doe',
            specialization='Hematology',
            verified=True
        )
        self.patient = User.objects.create_user(
            username='patient1',
            email='patient@example.com',
            password='pass123',
            user_type='user'
        )

    def test_doctor_code_generation(self):
        self.assertIsNotNone(self.doctor.doctor_code)
        self.assertEqual(len(self.doctor.doctor_code), 8)
        self.assertTrue(self.doctor.doctor_code.isalnum())
        self.assertTrue(self.doctor.doctor_code.isupper())

    def test_unique_doctor_code(self):
        doctor2 = User.objects.create_user(
            username='doctor2',
            email='doctor2@example.com',
            password='pass123',
            user_type='doctor'
        )
        self.assertNotEqual(self.doctor.doctor_code, doctor2.doctor_code)

class LinkDoctorAPITestCase(APITestCase):
    def setUp(self):
        self.doctor = User.objects.create_user(
            username='doctor1',
            email='doctor@example.com',
            password='pass123',
            user_type='doctor',
            first_name='John',
            last_name='Doe',
            specialization='Hematology',
            verified=True
        )
        self.patient = User.objects.create_user(
            username='patient1',
            email='patient@example.com',
            password='pass123',
            user_type='user'
        )
        self.client.force_authenticate(user=self.patient)

    def test_link_doctor_success(self):
        response = self.client.post('/api/patients/link-doctor/', {'doctor_code': self.doctor.doctor_code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.assigned_doctor, self.doctor)
        self.assertTrue(DoctorAssignmentLog.objects.filter(patient=self.patient, doctor=self.doctor).exists())

    def test_link_doctor_invalid_code(self):
        response = self.client.post('/api/patients/link-doctor/', {'doctor_code': 'INVALID'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid doctor code or not available.', response.data['detail'])

    def test_link_doctor_unauthenticated(self):
        self.client.logout()
        response = self.client.post('/api/patients/link-doctor/', {'doctor_code': self.doctor.doctor_code})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_doctor_patients_endpoint(self):
        self.patient.assigned_doctor = self.doctor
        self.patient.save()
        self.client.force_authenticate(user=self.doctor)
        response = self.client.get('/api/doctor/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], self.patient.username)

    def test_remove_patient(self):
        self.patient.assigned_doctor = self.doctor
        self.patient.save()
        self.client.force_authenticate(user=self.doctor)
        response = self.client.delete(f'/api/doctor/patients/{self.patient.id}/remove/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.patient.refresh_from_db()
        self.assertIsNone(self.patient.assigned_doctor)
        self.assertTrue(DoctorAssignmentLog.objects.filter(
            patient=self.patient,
            doctor=self.doctor,
            source='doctor_removal'
        ).exists())
