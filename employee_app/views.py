from django.contrib.auth import login, logout
from django.contrib import messages
from django import forms
from django.shortcuts import render, redirect

from employee_app.forms import AddLeaveForm, EditLeaveForm, EditProfileInfoForm, EditPersonalInfoForm, \
    AddEducationInfoForm, EditEducationInfoForm, AddExperienceInfoForm, EditExperienceInfoForm, \
    EditEmergencyContactForm, AddEmergencyContactForm
# Create your views here.
from hrms_api.models import User, Holiday, Designation, Department, Leave, Task, Project, ProjectAssign, Technology, \
    Education_Info, Experience_Info, Emergency_Contact


def landing(request):
    return render(request, 'landing.html')


def EmployeeLogin(request):
    if request.method == "POST":
        employeephone = request.POST.get('employeephone')
        employeepassword = request.POST.get('employeepassword')
        try:
            user = User.objects.get(phone=employeephone,is_admin=False)
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


# @login_required(login_url="EmployeeLogin")
def EmployeeIndex(request):
    user = request.user
    task_list = Task.objects.filter(task_assign=user.id)
    project_list = ProjectAssign.objects.filter(employee_name=user.id)

    context = {
        'user': user,
        'task_list': task_list,
        'project_list':project_list,
    }

    return render(request, "employee/employee-dashboard.html", context)


def EmployeeListView(request):
    emp_list = User.objects.all()
    return render(request, "employee/employees_list.html",{'emp_list':emp_list})


# def day_month_year_converter(date1, date2):
#     start_date = date1
#     end_date = date2
#     total_day = end_date - start_date
#
#     years = total_day.days // 365
#     months = (total_day.days % 365) // 30
#     days = (total_day.days % 365) % 30
#     return years, months, days


def ProfileView(request, id):
    user_details = User.objects.get(id=id)
    view_education_info = Education_Info.objects.filter(employee=id).order_by('start_year')
    view_experience_info = Experience_Info.objects.filter(employee=id).order_by('start_date')
    view_emergency_contact = Emergency_Contact.objects.filter(employee=id)

    context = {
        'user_details': user_details,
        'view_education_info': view_education_info,
        'view_experience_info': view_experience_info,
        'view_emergency_contact':view_emergency_contact
    }
    return render(request, "employee/profile.html", context)


def EditProfileInfo(request, id):
    edit_profile_info = User.objects.get(id=id)
    form = EditProfileInfoForm(request.POST or None, request.FILES, instance=edit_profile_info)
    if request.method == 'POST':
        try:
            if form.is_valid():
                form.save()
                messages.info(request, 'Profile Info Update successfully')
                return redirect('EmpProfileView', id=id)
        except Exception as e:
            form = EditProfileInfoForm(instance=edit_profile_info)
    context = {'form': form, 'edit_profile_info': edit_profile_info}
    return render(request, "employee/edit_profile_info.html", context)


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
            form = EditPersonalInfoForm(instance=edit_personal_info)
    context = {'form': form, 'edit_personal_info': edit_personal_info}
    return render(request, "employee/edit_personal_info.html", context)


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
            form = AddEducationInfoForm()
    context = {'form': form}
    return render(request, "employee/add_education_info.html", context)


def EditEducationInfo(request, id, edu_id):
    edit_education_info = Education_Info.objects.filter(id=edu_id).first()
    form = EditEducationInfoForm(request.POST or None, instance=edit_education_info)
    if request.method == 'POST':
        try:
            if form.is_valid():
                education = form.save(commit=False)
                education.employee = User.objects.get(id=id)
                education.save()
                messages.info(request, 'Education Info Update successfully')
                return redirect('EmpProfileView', id=id)
        except Exception as e:
            form = EditEducationInfoForm(instance=edit_education_info)
    context = {'form': form, 'edit_education_info': edit_education_info}
    return render(request, "employee/edit_education_info.html", context)


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
            form = AddExperienceInfoForm()
    context = {'form': form}
    return render(request, "employee/add_experience_info.html", context)


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
            form = EditExperienceInfoForm(instance=edit_experience_info)
    context = {'form': form, 'edit_experience_info': edit_experience_info}
    return render(request, "employee/edit_experience_info.html", context)


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
            form = AddEmergencyContactForm()
    context = {'form': form}
    return render(request, "employee/add_emergency_contact.html", context)


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
            form = EditEmergencyContactForm(instance=edit_emergency_contact)
    context = {'form': form, 'edit_emergency_contact': edit_emergency_contact}
    return render(request, "employee/edit_emergency_contact.html", context)


def EmployeeLogout(request):
    logout(request)
    return render(request, "employee/login.html")


def Holidays(request):
    holidaylist = Holiday.objects.all().order_by('holiday_date')
    context = {
        'holidaylist': holidaylist,
    }
    return render(request, "employee/holidays_list.html", context)


def DepartmentView(request):
    departmentlist = Department.objects.all()
    context = {
        'departmentlist': departmentlist,
    }
    return render(request, "employee/departments.html", context)


def DesignationView(request):
    designationlist = Designation.objects.all()
    context = {
        'designationlist': designationlist,
    }
    return render(request, "employee/designations.html", context)


def TechnologyView(request):
    technologylist = Technology.objects.all()
    context = {
        'technologylist': technologylist,
    }
    return render(request, "employee/technology.html", context)


def Leaves(request, id):
    leave_list = Leave.objects.filter(leave_user=id)
    context = {
        'leave_list': leave_list
    }
    return render(request, "employee/leaves-employee.html", context)


def AddLeave(request, id):
    userid = User.objects.get(id=id)
    if request.method == 'POST':
        form = AddLeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.leave_user = User.objects.get(id=id)
            leave.save()
            messages.success(request, 'Leave added successfully')
            return redirect('EmpLeaves', id=userid.id)
    else:
        form = AddLeaveForm()
    context = {'form': form}
    return render(request, "employee/add_leave.html", context)


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
            form = EditLeaveForm(instance=edit_leave)
    context = {'form': form, 'edit_leave': edit_leave}
    return render(request, "employee/edit_leave.html", context)


def DeleteLeave(request, id):
    userid = request.user.id
    delete_leave = Leave.objects.get(id=id)
    delete_leave.delete()
    messages.error(request, 'Leave Delete successfully')
    return redirect('EmpLeaves', id=userid)
