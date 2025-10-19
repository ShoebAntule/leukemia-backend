from django.contrib.auth.models import AbstractUser
from django.db import models
import secrets
import string

def generate_doctor_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

class CustomUser(AbstractUser):
    USER_TYPES = [
        ('doctor', 'Doctor'),
        ('user', 'User'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='user')
    specialization = models.CharField(max_length=100, blank=True, null=True)
    verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    doctor_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    assigned_doctor = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='patients')

    def save(self, *args, **kwargs):
        if self.user_type == 'doctor' and not self.doctor_code:
            code = generate_doctor_code()
            while CustomUser.objects.filter(doctor_code=code).exists():
                code = generate_doctor_code()
            self.doctor_code = code
        super().save(*args, **kwargs)

class DoctorAssignmentLog(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assignment_logs')
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_patients_logs')
    source = models.CharField(max_length=32, default='doctor_code')
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.patient.username} assigned to {self.doctor.username} via {self.source}"
