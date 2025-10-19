from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'doctor', 'result', 'verified', 'created_at')
    list_filter = ('verified', 'created_at')
    search_fields = ('user__username', 'doctor__username', 'result')
