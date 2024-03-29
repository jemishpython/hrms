import datetime
import time
from datetime import date

from django.contrib.auth import login, logout
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template import loader
from django import forms
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect

from employee_app.forms import AddLeaveForm, EditLeaveForm, EditProfileInfoForm, EditPersonalInfoForm, \
    AddEducationInfoForm, EditEducationInfoForm, AddExperienceInfoForm, EditExperienceInfoForm, \
    EditEmergencyContactForm, AddEmergencyContactForm, AddTicketsForm, EditTicketsForm, PunchInForm, PunchOutForm
from hrms_api.choices import LeaveStatusChoice, TicketPriorityChoice, TicketStatusChoice, AttendanceStatusChoice
# Create your views here.
from hrms_api.models import User, Holiday, Designation, Department, Leave, Task, Project, ProjectAssign, Technology, \
    Education_Info, Experience_Info, Emergency_Contact, Ticket, Bank, TaskAssign, ProjectImages, ProjectFile, Policies, \
    Attendance


def landing(request):
    return render(request, 'landing.html')


def EmployeeLogin(request):
    if request.method == "POST":
        employeephone = request.POST.get('employeephone')
        employeepassword = request.POST.get('employeepassword')
        try:
            user = User.objects.get(phone=employeephone, is_admin=False)
        except:
            messages.error(request, "Login user is not Employee.", extra_tags='danger')
            return redirect('EmployeeLogin')
        if user.is_active:
            if user.check_password(employeepassword):
                login(request, user)
                return redirect('EmployeeIndex')
            messages.error(request, "Invalid credentials")
            return redirect('EmployeeLogin')
        messages.warning(request, "Please wait for admin is approve your request")
        return redirect('EmployeeLogin')
    return render(request, "employee/login.html")


def forget_password_mail(request):
    forget_password_phone = request.POST.get('employeephone')
    user = User.objects.filter(phone=forget_password_phone, is_active=True).first()

    forget_password_email = user.email

    context = {
        'username': user.username,
        'user_id': user.id,
        'request_url': request.get_host(), #For Liveproject
    }

    from_email = settings.EMAIL_HOST_USER
    mail_subject = f"HRMS Forget Password : {user.username}"

    email = loader.render_to_string('employee/forgot_password_email_template.html', context)
    send_mail(
        subject=mail_subject,
        message=email,
        from_email=from_email,
        recipient_list=[forget_password_email],
        html_message=email,
    )
    return redirect('EmployeeLogin')


def reset_page(request, pk):
    user = User.objects.get(id=pk)
    context = {
        'pk': pk,
        'user_id': user.id,
    }
    return render(request, 'employee/forgot_password.html', context)


def update_password(request, pk):
    user_pass = User.objects.get(id=pk)
    id = user_pass.id
    if request.method == 'POST':
        password = request.POST.get('employee_password')
        conf_password = request.POST.get('employee_confirm_password')
        if password == conf_password:
            user = User.objects.get(id=pk)
            user.password = make_password(password)
            user.save()
            return redirect('EmployeeLogin')
        else:
            messages.error(request, "Passwords do not match.")
            return redirect('emp_forgot_password', pk=id)
    else:
        return redirect('EmployeeLogin')


@login_required(login_url="EmployeeLogin")
def EmployeeIndex(request):
    user = request.user
    user_task = TaskAssign.objects.filter(employees=user)
    user_projects = ProjectAssign.objects.filter(employees=user)

    context = {
        'user': user,
        'user_task': user_task,
        'user_projects': user_projects,
    }

    return render(request, "employee/employee-dashboard.html", context)


@login_required(login_url="EmployeeLogin")
def EmployeeListView(request):
    emp_list = User.objects.all()
    emp_technology = Technology.objects.all()
    emp_department = Department.objects.all()
    emp_designation = Designation.objects.all()
    context = {
        'emp_list': emp_list,
        'emp_technology': emp_technology,
        'emp_department': emp_department,
        'emp_designation': emp_designation,
    }
    return render(request, "employee/employees_list.html", context)


# def day_month_year_converter(date1, date2):
#     start_date = date1
#     end_date = date2
#     total_day = end_date - start_date
#
#     years = total_day.days // 365
#     months = (total_day.days % 365) // 30
#     days = (total_day.days % 365) % 30
#     return years, months, days


@login_required(login_url="EmployeeLogin")
def ProfileView(request, id):
    user_details = User.objects.get(id=id)
    view_education_info = Education_Info.objects.filter(employee=id).order_by('start_year')
    view_experience_info = Experience_Info.objects.filter(employee=id).order_by('start_date')
    view_emergency_contact = Emergency_Contact.objects.filter(employee=id).first()
    view_bank_info = Bank.objects.filter(employee=id).first()

    context = {
        'user_details': user_details,
        'view_education_info': view_education_info,
        'view_experience_info': view_experience_info,
        'view_emergency_contact': view_emergency_contact,
        'view_bank_info': view_bank_info,
    }
    return render(request, "employee/profile.html", context)


@login_required(login_url="EmployeeLogin")
def EditProfileInfo(request, id):
    edit_profile_info = User.objects.get(id=id)
    form = EditProfileInfoForm(request.POST or None, request.FILES or None, instance=edit_profile_info)
    if request.method == 'POST':
        try:
            if form.is_valid():
                form.save()
                messages.info(request, 'Profile Info Update successfully')
                return redirect('EmpProfileView', id=id)
        except Exception as e:
            messages.error(request, 'ERROR : ', e)
    context = {'form': form, 'edit_profile_info': edit_profile_info}
    return render(request, "employee/edit_profile_info.html", context)


@login_required(login_url="EmployeeLogin")
def EditPersonalInfo(request, id):
    edit_personal_info = User.objects.get(id=id)
    form = EditPersonalInfoForm(request.POST or None, instance=edit_personal_info)
    if request.method == 'POST':
        try:
            if form.is_valid():
                form.save()
                messages.info(request, 'Personal Info Update successfully')
                return redirect('EmpProfileView', id=id)
        except Exception as e:
            messages.error(request, 'ERROR : ', e)
    context = {'form': form, 'edit_personal_info': edit_personal_info}
    return render(request, "employee/edit_personal_info.html", context)


@login_required(login_url="EmployeeLogin")
def AddEducationInfo(request, id):
    form = AddEducationInfoForm(request.POST or None)
    if request.method == 'POST':
        try:
            if form.is_valid():
                education = form.save(commit=False)
                education.employee = User.objects.get(id=id)
                education.save()
                messages.success(request, 'Education Info Add successfully')
                return redirect('EmpProfileView', id=id)
        except Exception as e:
            messages.error(request, 'ERROR : ', e)
    context = {'form': form}
    return render(request, "employee/add_education_info.html", context)


@login_required(login_url="EmployeeLogin")
def EmpEditEducationInfo(request, id, edu_id):
    edit_education_info = Education_Info.objects.filter(id=edu_id).first()
    form = EditEducationInfoForm(request.POST or None, instance=edit_education_info)
    if request.method == 'POST':
        try:
            if form.is_valid():
                form.save()
                messages.info(request, 'Education Info Update successfully')
                return redirect('EmpProfileView', id=id)
        except Exception as e:
            messages.error(request, 'ERROR : ', e)
    context = {'form': form, 'edit_education_info': edit_education_info}
    return render(request, "employee/edit_education_info.html", context)


@login_required(login_url="EmployeeLogin")
def DeleteEducation(request, id, edu_id):
    user_id = User.objects.get(id=id)
    delete_edu = Education_Info.objects.get(id=edu_id)
    delete_edu.delete()
    messages.error(request, 'Education information Delete successfully')
    return redirect('EmpProfileView', id=user_id.id)


@login_required(login_url="EmployeeLogin")
def AddExperienceInfo(request, id):
    form = AddExperienceInfoForm(request.POST or None)
    if request.method == 'POST':
        try:
            if form.is_valid():
                experience = form.save(commit=False)
                experience.employee = User.objects.get(id=id)
                experience.save()
                messages.success(request, 'Experience Info Add successfully')
                return redirect('EmpProfileView', id=id)
        except Exception as e:
            messages.error(request, 'ERROR : ', e)
    context = {'form': form}
    return render(request, "employee/add_experience_info.html", context)


@login_required(login_url="EmployeeLogin")
def EditExperienceInfo(request, id, exp_id):
    edit_experience_info = Experience_Info.objects.filter(id=exp_id).first()
    form = EditExperienceInfoForm(request.POST or None, instance=edit_experience_info)
    if request.method == 'POST':
        try:
            if form.is_valid():
                experience = form.save(commit=False)
                experience.employee = User.objects.get(id=id)
                experience.save()
                messages.info(request, 'Experience Info Update successfully')
                return redirect('EmpProfileView', id=id)
        except Exception as e:
            messages.error(request, 'ERROR : ', e)
    context = {'form': form, 'edit_experience_info': edit_experience_info}
    return render(request, "employee/edit_experience_info.html", context)


@login_required(login_url="EmployeeLogin")
def DeleteExperience(request, id, exp_id):
    user_id = User.objects.get(id=id)
    delete_exp = Experience_Info.objects.get(id=exp_id)
    delete_exp.delete()
    messages.error(request, 'Experience information Delete successfully')
    return redirect('EmpProfileView', id=user_id.id)


@login_required(login_url="EmployeeLogin")
def AddEmergencyInfo(request, id):
    form = AddEmergencyContactForm(request.POST or None)
    if request.method == 'POST':
        try:
            if form.is_valid():
                emergency_contact = form.save(commit=False)
                emergency_contact.employee = User.objects.get(id=id)
                emergency_contact.save()
                messages.success(request, 'Experience Info Add successfully')
                return redirect('EmpProfileView', id=id)
        except Exception as e:
            messages.error(request, 'ERROR : ', e)
    context = {'form': form}
    return render(request, "employee/add_emergency_contact.html", context)


@login_required(login_url="EmployeeLogin")
def EditEmergencyInfo(request, id, emg_id):
    edit_emergency_contact = Emergency_Contact.objects.get(id=emg_id)
    form = EditEmergencyContactForm(request.POST or None, instance=edit_emergency_contact)
    if request.method == 'POST':
        try:
            if form.is_valid():
                emergency_contact = form.save(commit=False)
                emergency_contact.employee = User.objects.get(id=id)
                emergency_contact.save()
                messages.info(request, 'Experience Info Update successfully')
                return redirect('EmpProfileView', id=id)
        except Exception as e:
            messages.error(request, 'ERROR : ', e)
    context = {'form': form, 'edit_emergency_contact': edit_emergency_contact}
    return render(request, "employee/edit_emergency_contact.html", context)


@login_required(login_url="EmployeeLogin")
def DeleteEmergency(request, id, emg_id):
    user_id = User.objects.get(id=id)
    delete_emg = Emergency_Contact.objects.get(id=emg_id)
    delete_emg.delete()
    messages.error(request, 'Emergency information Delete successfully')
    return redirect('EmpProfileView', id=user_id.id)


@login_required(login_url="EmployeeLogin")
def EmployeeLogout(request):
    logout(request)
    return render(request, "employee/login.html")


@login_required(login_url="EmployeeLogin")
def Holidays(request):
    year = date.today()
    holidaylist = Holiday.objects.all().order_by('holiday_date')
    context = {
        'holidaylist': holidaylist,
        'year': year,
    }
    return render(request, "employee/holidays_list.html", context)


@login_required(login_url="EmployeeLogin")
def DepartmentView(request):
    departmentlist = Department.objects.all()
    context = {
        'departmentlist': departmentlist,
    }
    return render(request, "employee/departments.html", context)


@login_required(login_url="EmployeeLogin")
def DesignationView(request):
    designationlist = Designation.objects.all()
    context = {
        'designationlist': designationlist,
    }
    return render(request, "employee/designations.html", context)


@login_required(login_url="EmployeeLogin")
def TechnologyView(request):
    technologylist = Technology.objects.all()
    context = {
        'technologylist': technologylist,
    }
    return render(request, "employee/technology.html", context)


@login_required(login_url="EmployeeLogin")
def Leaves(request, id):
    leave_list = Leave.objects.filter(leave_user=id)
    new_leaves_count = leave_list.filter(leave_status=LeaveStatusChoice.NEW).count()
    approved_leaves_count = leave_list.filter(leave_status=LeaveStatusChoice.APPROVED).count()
    decline_leaves_count = leave_list.filter(leave_status=LeaveStatusChoice.DECLINED).count()
    remaining_leaves_count = (12 - approved_leaves_count)
    leave_status = LeaveStatusChoice.choices
    context = {
        'leave_list': leave_list,
        'leave_status': leave_status,
        'new_leaves_count': new_leaves_count,
        'approved_leaves_count': approved_leaves_count,
        'decline_leaves_count': decline_leaves_count,
        'remaining_leaves_count': remaining_leaves_count,
    }
    return render(request, "employee/leaves-employee.html", context)


@login_required(login_url="EmployeeLogin")
def AddLeave(request, id):
    userid = User.objects.get(id=id)
    form = AddLeaveForm(request.POST)
    if request.method == 'POST':
        try:
            if form.is_valid():
                leave = form.save(commit=False)
                leave.leave_user = User.objects.get(id=id)
                leave.save()
                messages.success(request, 'Leave added successfully')
                return redirect('EmpLeaves', id=userid.id)
            else:
                messages.error(request, 'Form Not Valid', form.errors)
        except Exception as e:
            messages.error(request, 'ERROR', e)
    context = {'form': form}
    return render(request, "employee/add_leave.html", context)


@login_required(login_url="EmployeeLogin")
def EditLeave(request, id, userid):
    userid = User.objects.get(id=userid)
    edit_leave = Leave.objects.get(id=id)
    form = EditLeaveForm(request.POST or None, instance=edit_leave)
    if request.method == 'POST':
        try:
            if form.is_valid():
                form.save()
                messages.info(request, 'Leave Update successfully')
                return redirect('EmpLeaves', id=userid.id)
        except Exception as e:
            messages.error(request, 'ERROR : ', e)
    context = {'form': form, 'edit_leave': edit_leave}
    return render(request, "employee/edit_leave.html", context)


@login_required(login_url="EmployeeLogin")
def DeleteLeave(request, id):
    userid = request.user.id
    delete_leave = Leave.objects.get(id=id)
    delete_leave.delete()
    messages.error(request, 'Leave Delete successfully')
    return redirect('EmpLeaves', id=userid)


@login_required(login_url="EmployeeLogin")
def Tickets(request, id):
    tickets_list = Ticket.objects.filter(ticket_user=id)
    new_tickets_count = tickets_list.filter(ticket_status=TicketStatusChoice.NEW).count()
    approved_tickets_count = tickets_list.filter(ticket_status=TicketStatusChoice.APPROVED).count()
    decline_tickets_count = tickets_list.filter(ticket_status=TicketStatusChoice.DECLINED).count()
    ticket_priority = TicketPriorityChoice.choices
    ticket_status = TicketStatusChoice.choices
    context = {
        'tickets_list': tickets_list,
        'new_tickets_count': new_tickets_count,
        'approved_tickets_count': approved_tickets_count,
        'decline_tickets_count': decline_tickets_count,
        'ticket_priority': ticket_priority,
        'ticket_status': ticket_status,
    }
    return render(request, "employee/employee-tickets.html", context)


@login_required(login_url="EmployeeLogin")
def AddTicket(request, id):
    userid = User.objects.get(id=id)
    form = AddTicketsForm(request.POST)
    if request.method == 'POST':
        try:
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.ticket_user = User.objects.get(id=id)
                ticket.save()
                messages.success(request, 'Ticket generate successfully')
                return redirect('EmpTickets', id=userid.id)
            else:
                messages.error(request, 'Form not valid : ', form.errors)
        except Exception as e:
            messages.error(request, 'ERROR', e)
    context = {'form': form}
    return render(request, "employee/add_tickets.html", context)


@login_required(login_url="EmployeeLogin")
def EditTicket(request, id, userid):
    userid = User.objects.get(id=userid)
    edit_tickets = Ticket.objects.get(id=id)
    form = EditTicketsForm(request.POST or None, instance=edit_tickets)
    if request.method == 'POST':
        try:
            if form.is_valid():
                form.save()
                messages.info(request, 'Ticket Update successfully')
                return redirect('EmpTickets', id=userid.id)
        except Exception as e:
            messages.error(request, 'ERROR', e)
    context = {'form': form, 'edit_tickets': edit_tickets}
    return render(request, "employee/edit_tickets.html", context)


@login_required(login_url="EmployeeLogin")
def DeleteTicket(request, id):
    userid = request.user.id
    delete_ticket = Ticket.objects.get(id=id)
    delete_ticket.delete()
    messages.error(request, 'Ticket Delete successfully')
    return redirect('EmpTickets', id=userid)


@login_required(login_url="EmployeeLogin")
def ChatView(request, id):
    return render(request, "employee/chat.html")


@login_required(login_url="EmployeeLogin")
def AttendanceView(request, id):
    current_datetime = datetime.datetime.now()
    attendee = Attendance.objects.filter(attendee_user=id)
    last_punchIn_id = Attendance.objects.filter(attendee_user=id).last()
    context = {
        'current_datetime': current_datetime,
        'attendee': attendee,
        'last_punchIn_id': last_punchIn_id,
    }
    return render(request, "employee/attendance-employee.html", context)


@login_required(login_url="EmployeeLogin")
def PunchIn(request, id):
    userid = User.objects.get(id=id)
    form = PunchInForm(request.POST)
    if request.method == 'POST':
        try:
            if form.is_valid():
                punchIn = form.save(commit=False)
                punchIn.date = date.today()
                punchIn.check_in_time = datetime.datetime.now().time()
                punchIn.attendee_user = User.objects.get(id=id)
                punchIn.save()
                messages.success(request, 'PunchIn successfully')
                return redirect('EmpAttendanceView', id=userid.id)
            else:
                messages.error(request, 'Form not valid : ', form.errors)
        except Exception as e:
            messages.error(request, 'ERROR', e)
    context = {'form': form}
    return render(request, "employee/attendance-employee.html", context)


# --------------------- Based on punchIn and punchOut time------------------------
@login_required(login_url="EmployeeLogin")
def PunchOut(request, id, userid):
    user_id = User.objects.get(id=userid)
    edit_attendance = Attendance.objects.get(id=id)
    form = PunchOutForm(request.POST or None, instance=edit_attendance)

    if request.method == 'POST':
        try:
            if form.is_valid():
                punchOut = form.save(commit=False)
                punchOut.check_out_time = datetime.datetime.now().time()
                production_time = datetime.datetime.combine(datetime.date.today(), punchOut.check_out_time) - datetime.datetime.combine(datetime.date.today(), punchOut.check_in_time)
                punchOut.production_hour = str(production_time)

                half_day_morning_end = datetime.time(13, 0)  # 1 PM
                half_day_evening_start = datetime.time(13, 0)  # 1 PM
                half_day_evening_end = datetime.time(18, 30)  # 6:30 PM
                full_day_start = datetime.time(8, 0)  # 8 AM
                full_day_end = datetime.time(18, 30)  # 6:30 PM

                if punchOut.check_in_time >= full_day_start and punchOut.check_out_time <= half_day_morning_end:
                    punchOut.attendance_status = AttendanceStatusChoice.HALF_DAY
                elif punchOut.check_in_time >= half_day_evening_start and punchOut.check_out_time <= half_day_evening_end:
                    punchOut.attendance_status = AttendanceStatusChoice.HALF_DAY
                elif punchOut.check_in_time >= full_day_start and punchOut.check_out_time <= full_day_end:
                    punchOut.attendance_status = AttendanceStatusChoice.PRESENT
                else:
                    punchOut.attendance_status = AttendanceStatusChoice.ABSENT

                punchOut.save()
                messages.success(request, 'PunchOut successfully')
                return redirect('EmpAttendanceView', id=user_id.id)
            else:
                messages.error(request, 'Form not valid: ' + str(form.errors))
        except Exception as e:
            messages.error(request, 'ERROR: ' + str(e))

    context = {'form': form}
    return render(request, "employee/attendance-employee.html", context)


# --------------------- Based on production time------------------------
#
#
# @login_required(login_url="EmployeeLogin")
# def PunchOut(request, id, userid):
#     user_id = User.objects.get(id=userid)
#     edit_attendance = Attendance.objects.get(id=id)
#     form = PunchOutForm(request.POST or None, instance=edit_attendance)
#
#     if request.method == 'POST':
#         try:
#             if form.is_valid():
#                 punchOut = form.save(commit=False)
#                 punchOut.check_out_time = datetime.datetime.now().time()
#                 production_time = datetime.datetime.combine(datetime.date.today(), punchOut.check_out_time) - datetime.datetime.combine(datetime.date.today(), punchOut.check_in_time)
#                 punchOut.production_hour = str(production_time)
#
#                 if production_time >= datetime.timedelta(hours=8, minutes=30):
#                     punchOut.attendance_status = AttendanceStatusChoice.PRESENT
#                 elif datetime.timedelta(hours=4) <= production_time < datetime.timedelta(hours=4, minutes=40):
#                     punchOut.attendance_status = AttendanceStatusChoice.HALF_DAY
#                 else:
#                     punchOut.attendance_status = AttendanceStatusChoice.ABSENT
#
#                 punchOut.save()
#
#                 messages.success(request, 'PunchOut successfully')
#                 return redirect('EmpAttendanceView', id=user_id.id)
#             else:
#                 messages.error(request, 'Form not valid: ' + str(form.errors))
#         except Exception as e:
#             messages.error(request, 'ERROR: ' + str(e))
#
#     context = {'form': form}
#     return render(request, "employee/attendance-employee.html", context)


@login_required(login_url="EmployeeLogin")
def ProjectView(request, id):
    user = request.user
    projectlist = ProjectAssign.objects.filter(employees=id)

    context = {
        'projectlist': projectlist,
        'user': user,
    }
    return render(request, "employee/projects.html", context)


@login_required(login_url="EmployeeLogin")
def ProjectDetailsView(request, id, user_id):
    projectdetailview = Project.objects.get(id=id)
    user_list = User.objects.all()
    project_leader_list = ProjectAssign.objects.filter(project_name=id, assignee_type='Leader')
    project_team_member_list = ProjectAssign.objects.filter(project_name=id, assignee_type='Team Member')
    project_images = ProjectImages.objects.filter(project_name=id)
    project_files = ProjectFile.objects.filter(project_name=id)
    project_task_list = TaskAssign.objects.filter(employees=user_id)

    context = {
        'projectdetailview': projectdetailview,
        'project_task_list': project_task_list,
        'user_list': user_list,
        'project_leader_list': project_leader_list,
        'project_team_member_list': project_team_member_list,
        'project_images': project_images,
        'project_files': project_files,
    }
    return render(request, "employee/project-view.html", context)


@login_required(login_url="EmployeeLogin")
def ProjectTaskView(request, id):
    projectlist = ProjectAssign.objects.filter(employees=id)

    context = {
        'projectlist': projectlist,
    }
    return render(request, "employee/task-nav.html", context)


@login_required(login_url="EmployeeLogin")
def ProjectTaskList(request, id, user_id):
    project_id = id
    project_list = ProjectAssign.objects.filter(employees=user_id)
    project_task_list = TaskAssign.objects.filter(employees=user_id)

    context = {
        'project_task_list': project_task_list,
        'project_list': project_list,
        'project_id': project_id,

    }
    return render(request, "employee/tasks.html", context)


@login_required(login_url="EmployeeLogin")
def PoliciesView(request):
    policies = Policies.objects.all()

    context = {
        'policies': policies,
    }
    return render(request, "employee/policies.html", context)


@login_required(login_url="EmployeeLogin")
def SalarySlip(request):
    return render(request, "employee/salary_slip.html")
