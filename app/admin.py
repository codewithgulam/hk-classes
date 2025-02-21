from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Session_Year, Student, Staff, Attendance, Attendance_Report, Fee

class UserModel(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'user_type', 'profile_pic', 'is_staff']

admin.site.register(CustomUser, UserModel)

@admin.register(Session_Year)
class SessionYearModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_start', 'session_end']

@admin.register(Student)
class StudentModelAdmin(admin.ModelAdmin):
    model = Student
    list_display = ['id', 'address', 'gender', 'join_data', 'mobile_number']

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['id', 'address', 'gender', 'mobile_number', 'created_at']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'attendance_date', 'session_year_id', 'created_at']

@admin.register(Attendance_Report)
class AttReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'student_id', 'attendance_id', 'created_at', 'updated_at']

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'amount', 'is_paid', 'created_at']

