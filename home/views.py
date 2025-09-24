from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import *

# -------------------------
# Role Mapping by Department
# -------------------------
ROLE_MAP = {
    "Engineering": Engineer,
    "Operations/Safety": OperationsUser,
    "Finance/Procurement": FinanceUser,
    "HR/Admin": HRUser,
    "Compliance/Legal": ComplianceUser,
    "Executive/Management": ExecutiveUser,
}

# -------------------------
# Role Models by Login Selection
# -------------------------
ROLE_MODELS = {
    "Engineer": Engineer,
    "OperationsUser": OperationsUser,
    "FinanceUser": FinanceUser,
    "HRUser": HRUser,
    "ComplianceUser": ComplianceUser,
    "ExecutiveUser": ExecutiveUser,
}

# -------------------------
# Home
# -------------------------
def home(request):
    return render(request, 'index.html')

# -------------------------
# Admin Dashboard: Create User
# -------------------------
def admin_dashboard(request):
    departments = Department.objects.all()
    message = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        dept_id = request.POST.get("department")

        if email and password and dept_id:
            if User.objects.filter(username=email).exists():
                message = "User with this email already exists."
            else:
                user = User.objects.create_user(username=email, email=email, password=password)
                department = Department.objects.get(id=dept_id)

                # Save user to the correct role model
                role_model = ROLE_MAP.get(department.name)
                if role_model:
                    role_model.objects.create(user=user)

                message = f"User {email} created successfully in {department.name}!"

    return render(request, 'admin_dashboard.html', {"departments": departments, "message": message})

# -------------------------
# User Login
# -------------------------
def user_login(request):
    error = None
    if request.method == "POST":
        role = request.POST.get("role")
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            role_model = ROLE_MODELS.get(role)
            if role_model and role_model.objects.filter(user=user).exists():
                login(request, user)
                return redirect("dashboard")
            else:
                error = "User does not belong to selected role."
        else:
            error = "Invalid username or password."

    return render(request, "login.html", {"error": error})

# -------------------------
# Dashboard
# -------------------------
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("user_login")
    return render(request, "dashboard.html", {"user": request.user})

# -------------------------
# Logout
# -------------------------
def user_logout(request):
    logout(request)
    return redirect("home")
