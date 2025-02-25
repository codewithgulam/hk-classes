from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime
# Create your models here.

class CustomUser(AbstractUser):
    USER = (
        (1, 'HOD'),
        (2, 'STAFF'),
        (3, 'STUDENT'),
    )
    user_type = models.CharField(choices=USER, max_length=50, default=1)
    profile_pic = models.ImageField(upload_to='media/profile_pic')


class School(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class Session_Year(models.Model):
    session_start = models.CharField(max_length=150)
    session_end = models.CharField(max_length=150)
    def __str__(self):
        return self.session_start + "     To    " + self.session_end

class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    gender = models.CharField(max_length=100)
    session_year_id = models.ForeignKey(Session_Year, on_delete=models.DO_NOTHING)
    join_data = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    def __str__(self):
        return self.admin.first_name + " " + self.admin.last_name

class Staff(models.Model):
    admin  = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    gender = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.admin.username

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    session_year_id = models.ForeignKey(Session_Year, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student.admin.first_name + " " + self.student.admin.last_name

class Attendance_Report(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student_id.admin.first_name + " " + self.student_id.admin.last_name

class Fee(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='fees')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)  # Allow null and blank values

    def __str__(self):
        return f"{self.student.admin.first_name} {self.student.admin.last_name} - {'Paid' if self.is_paid else 'Unpaid'}"

    class Meta:
        get_latest_by = 'created_at'

    def save(self, *args, **kwargs):
        if not self.due_date:
            join_date = datetime.strptime(self.student.join_data, '%Y-%m-%d')
            self.due_date = (join_date + relativedelta(days=30)).date()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_fees():
        students = Student.objects.all()
        today = datetime.today().date()
        for student in students:
            join_date = datetime.strptime(student.join_data, '%Y-%m-%d').date()
            next_due_date = join_date
            while next_due_date <= today:
                if not Fee.objects.filter(student=student, due_date=next_due_date).exists():
                    Fee.objects.create(student=student, amount=1000, due_date=next_due_date)  # Adjust the amount as needed
                next_due_date += timedelta(days=30)

