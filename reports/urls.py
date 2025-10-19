from django.urls import path
from . import views

urlpatterns = [
    path('reports/', views.ReportListView.as_view(), name='reports'),
    path('upload/', views.ReportUploadView.as_view(), name='upload'),
    path('verify-report/<int:pk>/', views.ReportVerifyView.as_view(), name='verify-report'),
    path('send-report-to-patient/<int:pk>/', views.SendReportToPatientView.as_view(), name='send-report-to-patient'),
    path('contact-doctor/', views.ContactDoctorView.as_view(), name='contact-doctor'),
    path('upload-patient-report/', views.UploadPatientReportView.as_view(), name='upload-patient-report'),
    path('doctor-reports/', views.DoctorPatientReportsView.as_view(), name='doctor-reports'),
    path('patient-reports/', views.PatientReportsView.as_view(), name='patient-reports'),
    path('verify-patient-report/<int:pk>/', views.VerifyPatientReportView.as_view(), name='verify-patient-report'),
    path('patient-messages/', views.PatientMessageListView.as_view(), name='patient-messages'),
    path('send-message/', views.PatientMessageCreateView.as_view(), name='send-message'),
    path('mark-message-read/<int:pk>/', views.PatientMessageMarkReadView.as_view(), name='mark-message-read'),
    path('create-report-from-analysis/', views.CreateReportFromAnalysisView.as_view(), name='create-report-from-analysis'),
    path('patient-microscopic-reports/', views.PatientMicroscopicReportsView.as_view(), name='patient-microscopic-reports'),
    path('doctor-report-stats/', views.DoctorReportStatsView.as_view(), name='doctor-report-stats'),
]
