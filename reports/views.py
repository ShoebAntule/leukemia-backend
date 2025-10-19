from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Report, PatientReport, PatientMessage
from .serializers import ReportSerializer, PatientReportUploadSerializer, PatientReportListSerializer, PatientMessageSerializer, PatientMessageCreateSerializer
from accounts.models import CustomUser
import requests
import os

class ReportListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'doctor':
            return Report.objects.all()
        else:
            return Report.objects.filter(user=user)

class ReportUploadView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        # Call FastAPI prediction
        image = self.request.FILES['image']
        files = {'file': image}
        response = requests.post('http://localhost:8000/predict', files=files)
        if response.status_code == 200:
            result = response.json()
            serializer.save(
                user=self.request.user,
                result=result['class'],
                gradcam_image=None  # For now, no gradcam
            )
        else:
            raise Exception("Prediction failed")

class ReportVerifyView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer
    queryset = Report.objects.all()

    def perform_update(self, serializer):
        if self.request.user.user_type != 'doctor':
            raise PermissionError("Only doctors can verify reports")
        serializer.save(doctor=self.request.user, verified=True)

class SendReportToPatientView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer
    queryset = Report.objects.all()

    def perform_update(self, serializer):
        from django.utils import timezone
        if self.request.user.user_type != 'doctor':
            raise PermissionError("Only doctors can send reports to patients")
        serializer.save(sent_to_patient=True, sent_at=timezone.now())

class ContactDoctorView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # Simple contact form - in real app, send email
        message = request.data.get('message')
        # For now, just return success
        return Response({"message": "Message sent successfully"}, status=status.HTTP_200_OK)

class UploadPatientReportView(generics.CreateAPIView):
    serializer_class = PatientReportUploadSerializer
    permission_classes = [IsAuthenticated]


class DoctorPatientReportsView(generics.ListAPIView):
    serializer_class = PatientReportListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'doctor':
            return PatientReport.objects.filter(doctor=user)
        return PatientReport.objects.none()

class PatientReportsView(generics.ListAPIView):
    serializer_class = PatientReportListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'user':
            return PatientReport.objects.filter(patient=user)
        return PatientReport.objects.none()

class VerifyPatientReportView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PatientReportListSerializer
    queryset = PatientReport.objects.all()

    def perform_update(self, serializer):
        if self.request.user.user_type != 'doctor':
            raise PermissionError("Only doctors can verify reports")
        serializer.save(verified=True, comments=self.request.data.get('comments', ''))

class PatientMessageListView(generics.ListAPIView):
    serializer_class = PatientMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'doctor':
            return PatientMessage.objects.filter(doctor=user)
        elif user.user_type == 'user':
            return PatientMessage.objects.filter(patient=user)
        return PatientMessage.objects.none()

class PatientMessageCreateView(generics.CreateAPIView):
    serializer_class = PatientMessageCreateSerializer
    permission_classes = [IsAuthenticated]

class PatientMessageMarkReadView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PatientMessageSerializer
    queryset = PatientMessage.objects.all()

    def perform_update(self, serializer):
        if self.request.user.user_type != 'doctor':
            raise PermissionError("Only doctors can mark messages as read")
        serializer.save(is_read=True)

class CreateReportFromAnalysisView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def create(self, request, *args, **kwargs):
        patients = request.POST.getlist('patients')
        image = request.FILES.get('image')
        result = request.POST.get('result')
        confidence = request.POST.get('confidence')

        if not patients or not image or not result:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.user_type != 'doctor':
            return Response({"error": "Only doctors can create reports from analysis"}, status=status.HTTP_403_FORBIDDEN)

        created_reports = []
        for patient_id in patients:
            try:
                patient = CustomUser.objects.get(id=patient_id, user_type='user')
                report = Report.objects.create(
                    user=patient,
                    image=image,
                    result=result,
                    verified=True,  # Since it's from doctor's analysis
                    doctor=request.user,
                    comments=f"Analysis confidence: {confidence}"
                )
                created_reports.append(report.id)
            except CustomUser.DoesNotExist:
                continue

        return Response({"created_reports": created_reports}, status=status.HTTP_201_CREATED)

class PatientMicroscopicReportsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReportSerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'user':
            return Report.objects.filter(user=user, verified=True, doctor__isnull=False)
        return Report.objects.none()

class DoctorReportStatsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if request.user.user_type != 'doctor':
            return Response({"error": "Only doctors can access this endpoint"}, status=status.HTTP_403_FORBIDDEN)

        # Get all reports for patients assigned to this doctor
        doctor_patients = CustomUser.objects.filter(assigned_doctor=request.user)

        # Count microscopic analysis reports (Report model)
        microscopic_reports = Report.objects.filter(user__in=doctor_patients)
        pending_microscopic = microscopic_reports.filter(verified=False).count()
        verified_microscopic = microscopic_reports.filter(verified=True).count()

        # Count uploaded PDF reports (PatientReport model)
        uploaded_reports = PatientReport.objects.filter(doctor=request.user)
        pending_uploaded = uploaded_reports.filter(verified=False).count()
        verified_uploaded = uploaded_reports.filter(verified=True).count()

        # Total counts
        total_pending = pending_microscopic + pending_uploaded
        total_verified = verified_microscopic + verified_uploaded

        return Response({
            "pending_reports": total_pending,
            "verified_reports": total_verified
        })
