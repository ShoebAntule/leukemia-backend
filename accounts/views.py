from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import permission_classes, api_view
from rest_framework.views import APIView
from .models import CustomUser, DoctorAssignmentLog
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, DoctorCodeLinkSerializer, DoctorBasicSerializer

class IsDoctor(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.user_type == 'doctor'

class IsPatient(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.user_type == 'user'

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })

class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class LinkDoctorView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = DoctorCodeLinkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'detail': 'Invalid doctor code or not available.'}, status=status.HTTP_400_BAD_REQUEST)

        doctor_code = serializer.validated_data['doctor_code'].upper()
        doctor = CustomUser.objects.filter(doctor_code=doctor_code, user_type='doctor').first()
        if not doctor:
            return Response({'detail': 'Invalid doctor code or not available.'}, status=status.HTTP_400_BAD_REQUEST)

        # Optional: check if doctor is verified
        # if not doctor.verified:
        #     return Response({'detail': 'Invalid doctor code or not available.'}, status=status.HTTP_400_BAD_REQUEST)

        patient = request.user
        if patient.user_type != 'user':
            return Response({'detail': 'Only patients can link to doctors.'}, status=status.HTTP_400_BAD_REQUEST)

        if patient.assigned_doctor == doctor:
            return Response({
                'message': 'Doctor already linked.',
                'doctor': DoctorBasicSerializer(doctor).data
            }, status=status.HTTP_200_OK)

        if patient.assigned_doctor and patient.assigned_doctor != doctor:
            return Response({'detail': 'Patient already assigned to another doctor.'}, status=status.HTTP_400_BAD_REQUEST)

        patient.assigned_doctor = doctor
        patient.save()

        DoctorAssignmentLog.objects.create(
            patient=patient,
            doctor=doctor,
            source='doctor_code'
        )

        return Response({
            'message': f'Doctor successfully linked. You will now see reports and messages from Dr. {doctor.first_name} {doctor.last_name}.',
            'doctor': DoctorBasicSerializer(doctor).data
        }, status=status.HTTP_200_OK)

class DoctorPatientsView(generics.ListAPIView):
    permission_classes = (IsDoctor,)
    serializer_class = UserSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(assigned_doctor=self.request.user)

@api_view(['DELETE'])
@permission_classes([IsDoctor])
def remove_patient(request, patient_id):
    try:
        patient = CustomUser.objects.get(id=patient_id, assigned_doctor=request.user)
        patient.assigned_doctor = None
        patient.save()
        DoctorAssignmentLog.objects.create(
            patient=patient,
            doctor=request.user,
            source='doctor_removal',
            note='Removed by doctor'
        )
        return Response({'message': 'Patient removed successfully.'}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'detail': 'Patient not found or not assigned to you.'}, status=status.HTTP_404_NOT_FOUND)
