from django.db import models
from accounts.models import CustomUser

class Report(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reports')
    doctor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_reports')
    image = models.ImageField(upload_to='uploads/')
    result = models.CharField(max_length=100)
    gradcam_image = models.ImageField(upload_to='gradcam/', blank=True, null=True)
    verified = models.BooleanField(default=False)
    sent_to_patient = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, null=True)

class PatientMessage(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.patient.username} to {self.doctor.username}: {self.subject}"

class PatientReport(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploaded_reports')
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_reports')
    report_file = models.FileField(upload_to='reports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Report by {self.patient.username} for {self.doctor.username}"
