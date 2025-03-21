from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from app.models import School, Session_Year, Student,CustomUser, Staff, Fee , Attendance, Attendance_Report
from django.contrib import messages
from django.db import models
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count,Q
import openpyxl
from django.http import HttpResponse # Updated import
from django.db.models import Count
from datetime import date, timedelta
from django.core.paginator import Paginator
from collections import defaultdict
from app.models import Fee

def get_fees_due_soon():
    today = date.today()
    due_date_threshold = today + timedelta(days=7)
    fees_due_soon = Fee.objects.filter(due_date__lte=due_date_threshold, is_paid=False)
    return fees_due_soon

@staff_member_required(redirect_field_name='next', login_url='login')
def HOME(request):
    student_count = Student.objects.filter(admin__user_type=3).count()
    staff_count = Staff.objects.filter(admin__user_type=2).count()
    school_count = School.objects.all().count()
    student_gender_male = Student.objects.filter(admin__user_type=3, gender='Male').count()
    student_gender_female = Student.objects.filter(admin__user_type=3, gender='Female').count()
    student_gender_other = Student.objects.filter(admin__user_type=3, gender='Other').count()

    # Calculate the school with the highest number of students
    school_with_highest_students = Student.objects.values('school__name').annotate(student_count=Count('id')).order_by('-student_count').first()

    # Get fees due soon
    fees_due_soon = get_fees_due_soon()

    context = {
        'student_count': student_count,
        'staff_count': staff_count,
        'course_count': school_count,
        'student_gender_male': student_gender_male,
        'student_gender_female': student_gender_female,
        'student_gender_other': student_gender_other,
        'school_with_highest_students': school_with_highest_students['school__name'] if school_with_highest_students else 'N/A',
        'highest_student_count': school_with_highest_students['student_count'] if school_with_highest_students else 0,
        'fees_due_soon': fees_due_soon,
    }
    return render(request, 'Hod/home.html', context)

@staff_member_required(redirect_field_name='next', login_url='login')
def ADD_STUDENT(request):
    schools = School.objects.all()
    session_years = Session_Year.objects.all()

    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        school_id = request.POST.get('school_id')
        session_year_id = request.POST.get('session_year_id')
        join_date = request.POST.get('join_date')
        mobile_number = request.POST.get('mobile_number')
        fee_amount = request.POST.get('fee_amount')

        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email Is Already Taken')
            context = {
                'schools': schools,
                'session_years': session_years,
                'profile_pic': profile_pic,
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'password': password,
                'address': address,
                'gender': gender,
                'school_id': school_id,
                'session_year_id': session_year_id,
                'join_date': join_date,
                'mobile_number': mobile_number,
                'fee_amount': fee_amount,
            }
            return render(request, 'Hod/add_student.html', context)
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username Is Already Taken')
            context = {
                'schools': schools,
                'session_years': session_years,
                'profile_pic': profile_pic,
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'password': password,
                'address': address,
                'gender': gender,
                'school_id': school_id,
                'session_year_id': session_year_id,
                'join_date': join_date,
                'mobile_number': mobile_number,
                'fee_amount': fee_amount,
            }
            return render(request, 'Hod/add_student.html', context)
        else:
            user = CustomUser(first_name=first_name, last_name=last_name, username=username, email=email, profile_pic=profile_pic, user_type=3)
            user.set_password(password)
            user.save()
            school_instance = School.objects.get(id=school_id)
            session_year_instance = Session_Year.objects.get(id=session_year_id)
            student = Student(admin=user, address=address, session_year_id=session_year_instance, school=school_instance, gender=gender, join_data=join_date, mobile_number=mobile_number)
            student.save()
            # Create a Fee instance for the student
            Fee.objects.create(student=student, amount=fee_amount)
            messages.success(request, user.first_name + " " + user.last_name + " Are Successfully Added. !!!")
            return redirect('add_student')

    context = {
        'schools': schools,
        'session_years': session_years,
    }
    return render(request, 'Hod/add_student.html', context)

@staff_member_required(redirect_field_name='next', login_url='login')
def VIEW_STUDENT(request):
    students = Student.objects.filter(admin__user_type=3)
    # Fetch the fee data for each student
    for student in students:
        fee = Fee.objects.filter(student=student).first()
        student.fee_amount = fee.amount if fee else 0

    context = {
        'students': students
    }
    return render(request, 'Hod/view_student.html', context)


@staff_member_required(redirect_field_name='next', login_url='login')
def UPDATE_STUDENT(request):
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        school_id = request.POST.get('school_id')
        session_year_id = request.POST.get('session_year_id')
        join_date = request.POST.get('join_date')
        mobile_number = request.POST.get('mobile_number')
        fee_amount = request.POST.get('fee_amount')

        user = CustomUser.objects.get(id=student_id)
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        if profile_pic:
            user.profile_pic = profile_pic
        user.save()

        student = Student.objects.get(admin=student_id)
        student.address = address
        student.gender = gender
        school = School.objects.get(id=school_id)
        student.school = school
        session_year = Session_Year.objects.get(id=session_year_id)
        student.session_year_id = session_year
        student.join_data = join_date
        student.mobile_number = mobile_number
        student.save()

        # Update the fee amount for the student
        fee = Fee.objects.filter(student=student).first()
        if fee:
            fee.amount = fee_amount
            fee.save()
        else:
            Fee.objects.create(student=student, amount=fee_amount)

        messages.success(request, 'Data Updated successfully. !!!')
        return redirect('view_student')
    else:
        messages.error(request, 'Failed to update student data. Please try again.')
        return redirect('edit_student', student_id=student_id)


@staff_member_required(redirect_field_name='next', login_url='login')
def DELETE_STUDENT(request, admin):
    student = CustomUser.objects.get(id = admin)
    student.delete()
    messages.success(request, 'Record is delete successfully. !!!')
    return redirect('view_student')
    return render(request, 'Hod/view_student.html')
#student Profile 

@login_required(login_url='/')
def student_profile(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    attendance_reports = Attendance_Report.objects.filter(student_id=student)
    fee_records = Fee.objects.filter(student=student)

    # Group attendance records by month and calculate counts
    attendance_by_month = defaultdict(lambda: {'present': 0, 'absent': 0})
    for report in attendance_reports:
        month = report.attendance_id.attendance_date.strftime('%B %Y')
        if report.status == 'Present':
            attendance_by_month[month]['present'] += 1
        else:
            attendance_by_month[month]['absent'] += 1

    # Paginate the attendance records by month
    paginator = Paginator(list(attendance_by_month.items()), 3)  # Show 3 months per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'student': student,
        'attendance_by_month': attendance_by_month,
        'page_obj': page_obj,
        'fee_records': fee_records,
    }
    return render(request, 'Hod/student_profile.html', context)
    

@staff_member_required(redirect_field_name='next', login_url='login')
def ADD_SCHOOL(request):
    if request.method == "POST":
        school_name = request.POST.get('course_name')
        # Create an instance of the School model
        school = School(name=school_name)
        # Save the instance to the database
        school.save()
        messages.success(request, 'School added successfully. !!!')
        return redirect('view_school')
    return render(request, 'Hod/add_course.html')

@staff_member_required(redirect_field_name='next', login_url='login')
def VIEW_SCHOOL(request):
    # course = Class.objects.all()
    school = School.objects.all()
    context = {
        'school':school
    }
    return render(request, 'Hod/view_course.html', context)

@staff_member_required(redirect_field_name='next', login_url='login')
def EDIT_SCHOOL(request,id):
    school = School.objects.get(id=id)
    context = {
        'school':school
    }
    return render(request, 'Hod/edit_course.html', context)

@staff_member_required(redirect_field_name='next', login_url='login')
def UPDATE_SCHOOL(request):
    if request.method == "POST":
        name = request.POST.get('course_name')
        course_id = request.POST.get('course_id')
        # print(course_name,course_id)
        school = School.objects.get(id = course_id)
        school.name = name
        school.save()
        messages.success(request, "Course Updated Successfully !!!.")
        return redirect('view_course')
    return render(request, 'Hod/edit_course.html')

@staff_member_required(redirect_field_name='next', login_url='login')
def DELETE_SCHOOL(request, id):
    school = School.objects.get(id = id)
    school.delete()
    messages.success(request, 'Course Is deleted Successfully. !!!')
    return redirect('view_school')

@staff_member_required(redirect_field_name='next', login_url='login')
def ADD_STAFF(request):
    if request.method == 'POST':
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        mobile_number = request.POST.get('mobile_number')

        if CustomUser.objects.filter(email= email).exists():
            messages.warning(request, 'Email is already Exists. !!!')
            return redirect('add_staff')
        if CustomUser.objects.filter(username= username).exists():
            messages.warning(request, 'Username is already Exists. !!!')
            return redirect('add_staff')
        else:
            user = CustomUser(user_type=2 ,first_name=first_name, last_name=last_name, username=username, email=email,profile_pic=profile_pic)
            user.set_password(password)
            user.save()

            staff = Staff(admin = user ,address=address, gender=gender, mobile_number=mobile_number)
            staff.save()
            messages.success(request, 'Staff Add is Successful. !!!')
            return redirect('add_staff')
        # print(profile_pic, first_name, last_name, username, email, password, address, gender, mobile_number)
    return render(request, 'Hod/add_staff.html')

@staff_member_required(redirect_field_name='next', login_url='login')
def VIEW_STAFF(request):
    staff = Staff.objects.all()
    context = {
        'staff': staff
    }
    return render(request, 'Hod/view_staff.html', context)

@staff_member_required(redirect_field_name='next', login_url='login')
def EDIT_STAFF(request, id):
    staff = Staff.objects.get(id=id)
    context = {
        'staff':staff
    }
    return render(request, 'Hod/edit_staff.html', context)

@staff_member_required(redirect_field_name='next', login_url='login')
def UPDATE_STAFF(request):
    if request.method == "POST":
        id = request.POST.get('staff_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        mobile_number = request.POST.get('mobile_number')
        profile_pic = request.POST.get('profile_pic')
        password = request.POST.get('password')

        user = CustomUser.objects.get(id = id)
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        if password != None and password != "":
            user.password = password
        if profile_pic != None and profile_pic != "":
            user.profile_pic = profile_pic
        user.save()
        staff  = Staff.objects.get(admin=id)
        staff.address = address
        staff.gender = gender
        staff.mobile_number = mobile_number
        staff.save()
        messages.success(request, 'Staff is Updated successful. !!!')
        return redirect('view_staff')

    return render(request, 'Hod/edit_staff.html')

@staff_member_required(redirect_field_name='next', login_url='login')
def DELETE_STAFF(request, id):
    staff = CustomUser.objects.get(id= id)
    staff.delete()
    messages.success(request, 'Staff is Deleted Successful. !!!')
    return redirect('view_staff')

    return render(request, 'Hod/view_staff.html')

# @staff_member_required(redirect_field_name='next', login_url='login')
# def ADD_SUBJECT(request):
#     course = Course.objects.all()
#     staff = Staff.objects.all()

#     if request.method == 'POST':
#         subject_name = request.POST.get('subject_name')
#         course_id = request.POST.get('course_id')
#         staff_id = request.POST.get('staff_id')

#         course = Course.objects.get(id = course_id)
#         staff = Staff.objects.get(id = staff_id)

#         subject = Subject(name = subject_name, course=course, staff= staff)
#         subject.save()
#         messages.success(request, "Subject Add Successfully. !!!")
#         return redirect('add_subject')
#     context = {
#         'course': course,
#         'staff': staff
#     }
#     return render(request, 'Hod/add_subject.html', context)

# @staff_member_required(redirect_field_name='next', login_url='login')
# def VIEW_SUBJECT(request):
#     subject = Subject.objects.all()
#     context = {
#         'subject':subject
#     }
#     return render(request, 'Hod/view_subject.html', context)

# @staff_member_required(redirect_field_name='next', login_url='login')
# def EDIT_SUBJECT(request, id):
#     subject = Subject.objects.get(id = id)
#     course = Course.objects.all()
#     staff = Staff.objects.all()
#     context = {
#         'subject': subject,
#         'course':course,
#         'staff':staff
#     }
#     return render(request, 'Hod/edit_subject.html', context)

# @staff_member_required(redirect_field_name='next', login_url='login')
# def UPDATE_SUBJECT(request):
#     if request.method == "POST":
#         subject_id = request.POST.get('subject_id')
#         name = request.POST.get('subject_name')
#         course_id = request.POST.get('course_id')
#         staff_id = request.POST.get('staff_id')
#         print(subject_id,name, course_id, staff_id)
#         course = Course.objects.get(id = course_id)
#         staff = Staff.objects.get(id = staff_id)

#         subject = Subject.objects.get(id= subject_id)
#         subject.name = name
#         subject.course = course
#         subject.staff = staff
#         subject.save()
#         messages.success(request, 'Subject Updated successful. !!!')
#         return redirect('view_subject')
#     return render(request, 'Hod/view_subject.html')

# @staff_member_required(redirect_field_name='next', login_url='login')
# def DELETE_SUBJECT(request, id):
#     subject = Subject.objects.filter(id = id)
#     subject.delete()
#     messages.success(request, 'Subject Deleted successfully. !!!')
#     return redirect('view_subject')

@staff_member_required(redirect_field_name='next', login_url='login')
def ADD_SESSION(request):
    if request.method == "POST":
        session_year_start = request.POST.get('session_year_start')
        session_year_end = request.POST.get('session_year_end')
        session = Session_Year(session_start=session_year_start, session_end=session_year_end)
        session.save()
        messages.success(request, "Session Add successfully.!!!")
        return redirect('add_session')
    return render(request, 'Hod/add_session.html')

@staff_member_required(redirect_field_name='next', login_url='login')
def VIEW_SESSION(request):
    session = Session_Year.objects.all()
    return render(request, 'Hod/view_session.html', {'session':session})

@staff_member_required(redirect_field_name='next', login_url='login')
def EDIT_SESSION(request,id):
    session = Session_Year.objects.filter(id = id)
    context = {
        'session':session
    }
    return render(request, 'Hod/edit_session.html', context)

@staff_member_required(redirect_field_name='next', login_url='login')
def UPDATE_SESSION(request):
    if request.method == "POST":
        session_id = request.POST.get('session_id')
        session_year_start = request.POST.get('session_year_start')
        session_year_end = request.POST.get('session_year_end')
        session = Session_Year(id = session_id, session_start= session_year_start, session_end = session_year_end)
        session.save()
        messages.success(request, 'Session Updated Successfully. !!!')
        return redirect('view_session')

    return render(request, 'Hod/view_session.html')

@staff_member_required(redirect_field_name='next', login_url='login')
def DELETE_SESSION(request, id):
    session = Session_Year.objects.get(id = id)
    session.delete()
    messages.success(request, 'Session Deleted Successfully. !!!')
    return redirect('view_session')



# Attandence views

@staff_member_required(redirect_field_name='next', login_url='login')
def MARK_ATTENDANCE(request):
    students = Student.objects.filter(admin__user_type=3)  # Filter only students
    sessions = Session_Year.objects.all()
    if request.method == 'POST':
        date = request.POST.get('attendance_date')
        session_year_id = request.POST.get('session_year_id')
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            # Check if attendance already exists for the student on the given date and session year
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                attendance_date=date,
                session_year_id_id=session_year_id
            )
            # Check if attendance report already exists for the student
            attendance_report, created = Attendance_Report.objects.get_or_create(
                student_id=student,
                attendance_id=attendance
            )
            # Update the status of the attendance report
            attendance_report.status = 'Present' if status == 'present' else 'Absent'
            attendance_report.save()
        messages.success(request, 'Attendance marked successfully.')
        return redirect('mark_attendance')
    return render(request, 'Hod/mark_attendance.html', {'students': students, 'sessions': sessions})



@staff_member_required(redirect_field_name='next', login_url='login')
def VIEW_ATTENDANCE(request):
    sessions = Session_Year.objects.all()
    attendance_records = None
    entered_date = None
    entered_session_year_id = None

    if request.method == 'POST':
        entered_date = request.POST.get('attendance_date')
        entered_session_year_id = request.POST.get('session_year_id')
        attendance_records = Attendance_Report.objects.filter(
            attendance_id__attendance_date=entered_date,
            attendance_id__session_year_id_id=entered_session_year_id,
            student_id__admin__user_type=3  # Filter only students
        )

    return render(request, 'Hod/view_attendance.html', {
        'sessions': sessions,
        'attendance_records': attendance_records,
        'entered_date': entered_date,
        'entered_session_year_id': entered_session_year_id
    })


@staff_member_required(redirect_field_name='next', login_url='login')
def ATTENDANCE_SUMMARY(request):
    sessions = Session_Year.objects.all()
    summary_records = None
    entered_session_year_id = None
    entered_from_date = None
    entered_to_date = None

    if request.method == 'POST':
        entered_session_year_id = request.POST.get('session_year_id')
        entered_from_date = request.POST.get('from_date')
        entered_to_date = request.POST.get('to_date')
        summary_records = Attendance_Report.objects.filter(
            attendance_id__session_year_id_id=entered_session_year_id,
            attendance_id__attendance_date__range=[entered_from_date, entered_to_date]
        ).values(
            'student_id', 'student_id__admin__first_name', 'student_id__admin__last_name'
        ).annotate(
            total_present=Count('id', filter=Q(status='present')),
            total_absent=Count('id', filter=Q(status='absent'))
        )

        if 'export' in request.POST:
            return export_to_excel(summary_records, entered_from_date, entered_to_date)

    return render(request, 'Hod/attendance_summary.html', {
        'sessions': sessions,
        'summary_records': summary_records,
        'entered_session_year_id': entered_session_year_id,
        'entered_from_date': entered_from_date,
        'entered_to_date': entered_to_date
    })

def export_to_excel(summary_records, from_date, to_date):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = f"Attendance Summary {from_date} to {to_date}"

    # Add headers
    headers = ['ID', 'Name', 'Total Present', 'Total Absent']
    sheet.append(headers)

    # Add data
    for idx, record in enumerate(summary_records, start=1):
        row = [
            idx,
            f"{record['student_id__admin__first_name']} {record['student_id__admin__last_name']}",
            record['total_present'],
            record['total_absent']
        ]
        sheet.append(row)

    # Create a response object
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=attendance_summary_{from_date}_to_{to_date}.xlsx'
    workbook.save(response)
    return response


# Fee management
@login_required(login_url='/')
def FEE_LIST(request):
    # Generate fees for all students
    Fee.generate_fees()

    fees = Fee.objects.all()

    # Group fees by month
    fees_by_month = defaultdict(list)
    for fee in fees:
        month = fee.due_date.strftime('%B %Y')
        fees_by_month[month].append(fee)

    # Convert defaultdict to a regular dict for easier template handling
    fees_by_month = dict(fees_by_month)

    context = {
        'fees_by_month': fees_by_month,
    }
    return render(request, 'Hod/fee_list.html', context)


@login_required(login_url='/')
def VIEW_DUE_FEES(request):
    today = date.today()
    due_date_threshold = today + timedelta(days=7)
    fees_due_soon = Fee.objects.filter(due_date__lte=due_date_threshold, is_paid=False)

    # Group fees by month
    fees_by_month = defaultdict(list)
    for fee in fees_due_soon:
        month = fee.due_date.strftime('%B %Y')
        fees_by_month[month].append(fee)

    # Convert defaultdict to a regular dict for easier template handling
    fees_by_month = dict(fees_by_month)

    context = {
        'fees_by_month': fees_by_month,
    }
    return render(request, 'Hod/due_fees.html', context)

@login_required(login_url='/')
def MARK_FEE_PAID(request, fee_id):
    fee = get_object_or_404(Fee, id=fee_id)
    fee.is_paid = True
    fee.save()
    messages.success(request, "Fee marked as paid successfully!")
    return redirect('fee_list')

@login_required(login_url='/')
def MARK_FEE_UNPAID(request, fee_id):
    fee = get_object_or_404(Fee, id=fee_id)
    fee.is_paid = False
    fee.save()
    messages.success(request, "Fee marked as unpaid successfully!")
    return redirect('fee_list')

# This is a Staff Notification
# @staff_member_required(redirect_field_name='next', login_url='login')
# def STAFF_SEND_NOTIFICATION(request):
#     staff = Staff.objects.all()
#     see_notification  = Staff_Notification.objects.all().order_by('-id')[0:5]
#     context = {
#         'staff':staff,
#         'see_notification':see_notification
#     }
#     return render(request, 'Hod/staff_notification.html', context)

# @staff_member_required(redirect_field_name='next', login_url='login')
# def SAVE_STAFF_NOTIFICATION(request):
#     if request.method == "POST":
#         staff_id = request.POST.get('staff_id')
#         message = request.POST.get('message')
#         staff = Staff.objects.get(admin=staff_id)
#         notification = Staff_Notification(staff_id = staff, message = message)
#         notification.save()
#         messages.success(request, 'Message Send is successfully. !!!')
#         return redirect('staff_send_notification')
#     return render(request, 'Hod/staff_notification.html')

# @staff_member_required(redirect_field_name='next', login_url='login')
# def STAFF_LEAVE_VIEW(request):
#     staff_leave = Staff_Leave.objects.all()
#     context = {
#         'staff_leave':staff_leave
#     }
#     return render(request, 'Hod/staff_leave.html', context)


# @staff_member_required(redirect_field_name='next', login_url='login')
# def STAFF_APPROVE_LEAVE(request, id):
#     leave = Staff_Leave.objects.get(id = id)
#     leave.status = 1
#     leave.save()
#     return redirect('staff_leave_view')

# @staff_member_required(redirect_field_name='next', login_url='login')
# def STAFF_DISAPPROVE_LEAVE(request, id):
#     leave =Staff_Leave.objects.get(id = id)
#     leave.status = 2
#     leave.save()
#     return redirect('staff_leave_view')

# @staff_member_required(redirect_field_name='next', login_url='login')
# def STAFF_FEEDBACK(request):
#     feedback =Staff_Feedback.objects.all()
#     context={
#         "feedback":feedback,
#     }

#     return render(request, 'Hod/staff_feedback.html',context)


# @staff_member_required(redirect_field_name='next', login_url='login')
# def STAFF_FEEDBACK_SAVE(request):
#     if request.method == "POST":
#         feedback_id = request.POST.get('feedback_id')
#         feedback_reply = request.POST.get('feedback_reply')
#         feedback = Staff_Feedback.objects.get(id = feedback_id)
#         feedback.feedback_reply = feedback_reply
#         feedback.status = 1
#         feedback.save()
#         return redirect('staff_feedback_reply')

# @staff_member_required(redirect_field_name='next', login_url='login')
# def STUDENT_SEND_NOTIFICATION(request):
#     student = Student.objects.all()
#     notification = Student_Notification.objects.all()
#     context={
#         'student':student,
#         'notification':notification,
#     }

#     return render(request, 'Hod/student_notification.html', context)

# @staff_member_required(redirect_field_name='next', login_url='login')
# def SAVE_STUDENT_NOTIFICATION(request):
#     if request.method == "POST":
#         message = request.POST.get('message')
#         student_id = request.POST.get('student_id')
#         student = Student.objects.get(admin=student_id)
#         stud_notification = Student_Notification(student_id=student, message=message)
#         stud_notification.save()
#         messages.success(request, 'Student Notification Are send Successfully !!!')
#         return redirect('student_send_notification')

# @staff_member_required(redirect_field_name='next', login_url='login')
# def STUDENT_FEEDBACK(request):
#     feedback = Student_Feedback.objects.all().order_by('-id')[0:5]
#     context = {
#         'feedback':feedback
#     }
#     return render(request, 'Hod/student_feedback.html', context)

# @staff_member_required(redirect_field_name='next', login_url='login')
# def STUDENT_FEEDBACK_SAVE(request):
#     if request.method == "POST":
#         feedback_id = request.POST.get('feedback_id')
#         feedback_reply = request.POST.get('feedback_reply')
#         feedback = Student_Feedback.objects.get(id=feedback_id)
#         feedback.feedback_reply = feedback_reply
#         feedback.status = 1
#         feedback.save()
#         messages.success(request, 'Reply send successfully !!!')
#         return redirect('student_feedback_reply')

# @staff_member_required(redirect_field_name='next', login_url='login')
# def STUDENT_LEAVE_VIEW(request):
#     student_leave = Student_Leave.objects.all()
#     context = {
#         'student_leave':student_leave
#     }
#     return render(request, 'Hod/student_leave.html', context)

# @staff_member_required(redirect_field_name='next', login_url='login')
# def STUDENT_APPROVE_LEAVE(request, id):
#     leave = Student_Leave.objects.get(id=id)
#     leave.status = 1
#     leave.save()
#     return redirect('student_leave_view')

# @staff_member_required(redirect_field_name='next', login_url='login')
# def STUDENT_DISAPPROVE_LEAVE(request, id):
#     leave = Student_Leave.objects.get(id=id)
#     leave.status = 2
#     leave.save()
#     return redirect('student_leave_view')

# @staff_member_required(redirect_field_name='next', login_url='login')
# def VIEW_ATTENDANCE(request):
#     subject = Subject.objects.all()
#     session_year = Session_Year.objects.all()
#     action = request.GET.get('action')

#     get_session_year = None
#     get_subject = None
#     attendance_date = None
#     attendance_report = None
#     if action is not None:
#         if request.method == 'POST':
#             subject_id = request.POST.get('subject_id')
#             session_year_id = request.POST.get('session_year_id')
#             attendance_date = request.POST.get('attendance_date')

#             get_subject = Subject.objects.get(id=subject_id)
#             get_session_year = Session_Year.objects.get(id=session_year_id)
#             attendance = Attendance.objects.filter(subject_id=get_subject, attendance_date=attendance_date)
#             for i in attendance:
#                 attendance_id = i.id
#                 attendance_report = Attendance_Report.objects.filter(attendance_id=attendance_id)
#     context = {
#         'subject': subject,
#         'session_year': session_year,
#         'action': action,
#         'get_subject': get_subject,
#         'get_session_year': get_session_year,
#         'attendance_date': attendance_date,
#         'attendance_report': attendance_report
#     }
#     return render(request, 'Hod/view_attendance.html', context)

@staff_member_required(redirect_field_name='next', login_url='login')
def EDIT_STUDENT(request, student_id):
    student = Student.objects.get(id=student_id)
    schools = School.objects.all()
    session_years = Session_Year.objects.all()
    
    # Fetch the existing fee data for the student
    fee = Fee.objects.filter(student=student).first()
    fee_amount = fee.amount if fee else 0

    context = {
        'student': student,
        'schools': schools,
        'session_years': session_years,
        'fee_amount': fee_amount,
    }
    return render(request, 'Hod/edit_student.html', context)