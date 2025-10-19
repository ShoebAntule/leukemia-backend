from rest_framework import serializers
from .models import Report, PatientReport, PatientMessage
from accounts.models import CustomUser

class ReportSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    doctor_name = serializers.CharField(source='doctor.username', read_only=True)

    class Meta:
        model = Report
        fields = ('id', 'user', 'user_name', 'doctor', 'doctor_name', 'image', 'result', 'gradcam_image', 'verified', 'sent_to_patient', 'sent_at', 'created_at', 'comments')
        read_only_fields = ('user', 'doctor', 'created_at')

class PatientReportUploadSerializer(serializers.ModelSerializer):
    doctor_code = serializers.CharField(write_only=True)

    class Meta:
        model = PatientReport
        fields = ['id', 'report_file', 'doctor_code', 'uploaded_at']

    def create(self, validated_data):
        doctor_code = validated_data.pop('doctor_code')
        patient = self.context['request'].user
        try:
            doctor = CustomUser.objects.get(doctor_code=doctor_code, user_type='doctor')
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({'doctor_code': 'Invalid doctor code.'})
        validated_data['patient'] = patient
        validated_data['doctor'] = doctor
        return PatientReport.objects.create(**validated_data)


class PatientMessageSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.username', read_only=True)
    doctor_name = serializers.CharField(source='doctor.username', read_only=True)

    class Meta:
        model = PatientMessage
        fields = ['id', 'patient', 'patient_name', 'doctor', 'doctor_name', 'subject', 'message', 'priority', 'created_at', 'is_read']
        read_only_fields = ('patient', 'doctor', 'created_at')

class PatientMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientMessage
        fields = ['subject', 'message', 'priority']

    def create(self, validated_data):
        patient = self.context['request'].user
        doctor = patient.assigned_doctor
        if not doctor:
            raise serializers.ValidationError('You must be linked to a doctor to send messages.')
        validated_data['patient'] = patient
        validated_data['doctor'] = doctor
        return PatientMessage.objects.create(**validated_data)

class PatientReportListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.username', read_only=True)
    doctor_name = serializers.CharField(source='doctor.username', read_only=True)

    class Meta:
        model = PatientReport
        fields = ['id', 'patient_name', 'doctor_name', 'report_file', 'uploaded_at', 'verified', 'comments']
