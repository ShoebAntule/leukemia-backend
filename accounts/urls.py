from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('user/', views.UserDetailView.as_view(), name='user-detail'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user-detail-pk'),
    path('patients/link-doctor/', views.LinkDoctorView.as_view(), name='link-doctor'),
    path('doctor/patients/', views.DoctorPatientsView.as_view(), name='doctor-patients'),
    path('doctor/patients/<int:patient_id>/remove/', views.remove_patient, name='remove-patient'),
]
