from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DoctorAssignmentLog

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'specialization', 'verified', 'doctor_code', 'is_active')
    list_filter = ('user_type', 'verified', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'specialization', 'verified', 'doctor_code', 'assigned_doctor')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'specialization', 'verified', 'doctor_code', 'assigned_doctor')}),
    )

@admin.register(DoctorAssignmentLog)
class DoctorAssignmentLogAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'source', 'created_at')
    list_filter = ('source', 'created_at')
    readonly_fields = ('created_at',)
