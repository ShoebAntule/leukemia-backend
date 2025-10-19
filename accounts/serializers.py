from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'user_type', 'specialization', 'phone_number', 'date_of_birth', 'address')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type'],
            specialization=validated_data.get('specialization', ''),
            phone_number=validated_data.get('phone_number', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            address=validated_data.get('address', '')
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

class DoctorBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'specialization', 'verified', 'full_name')

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class UserSerializer(serializers.ModelSerializer):
    assigned_doctor = DoctorBasicSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'user_type', 'specialization', 'verified', 'phone_number', 'date_of_birth', 'address', 'doctor_code', 'assigned_doctor')

class DoctorCodeLinkSerializer(serializers.Serializer):
    doctor_code = serializers.CharField(max_length=12)
