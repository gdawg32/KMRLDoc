from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .doc_processor import process_and_classify
from django.conf import settings
import os


API_KEY = "API KEY HERE"
# -------------------------
# Role Mapping by Department
# -------------------------
ROLE_MAP = {
    "Technical": Engineer,
    "Operational": OperationsUser,
    "Financial": FinanceUser,
    "Administrative": HRUser,
    "Regulatory": ComplianceUser,
    "Executive": ExecutiveUser,
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

role_to_category = {
    "Finance": "Financial",
    "Operations": "Operational",
    "HR": "Administrative",
    "Compliance": "Regulatory",
    "Executive": "Executive",
    "Engineering": "Technical",
}

# -------------------------
# Home
# -------------------------
def home(request):
    return render(request, 'index.html')

# -------------------------
# Admin Dashboard and User Management
# -------------------------
def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin_dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid credentials or not an admin.")

    return render(request, "admin_login.html")

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("admin_login")
    
    departments = Department.objects.all()
    message = None
    documents = Document.objects.all()
    context = {
            "departments": departments,
            "message": message,
            "documents": documents,
        }

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
        
        

    return render(request, 'admin_dashboard.html', context)

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

def upload_documents(request):
    if request.method == "POST":
        files = request.FILES.getlist("files")
        department_name = request.POST.get("department")  

        if not files:
            messages.error(request, "No files selected for upload.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        for f in files:
            # Save file to media/documents/ temporarily
            upload_path = os.path.join(settings.MEDIA_ROOT, "documents", f.name)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)

            with open(upload_path, "wb+") as dest:
                for chunk in f.chunks():
                    dest.write(chunk)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            artifacts_dir = os.path.join(current_dir, "artifacts")

            try:
                # Process and classify
                result = process_and_classify(
                    file_path=upload_path,
                    artifacts_dir=artifacts_dir,
                    gemini_api_key=API_KEY,
                    translate=True
                )

                if department_name:
                    dept, _ = Department.objects.get_or_create(name=department_name)
                else:
                    dept = None  
                
                # Create Document record
                doc = Document.objects.create(
                    title=f.name,
                    uploaded_by=request.user,
                    department=dept,
                    file=f,  
                    extracted_text=result.get("extracted_text", ""),
                    translated_text=result.get("translated_text", ""),
                    summary=result.get("summary", ""),
                    processed=True
                )

                # Add predicted categories (labels)
                labels = result.get("predicted_labels", [])
                for label in labels:
                    cat, _ = Category.objects.get_or_create(name=label)
                    doc.categories.add(cat)

                doc.save()
            except Exception as e:
                messages.error(request, f"Error processing {f.name}: {str(e)}")
                return redirect(request.META.get("HTTP_REFERER", "/"))


        messages.success(request, "Files uploaded and processed successfully!")
        return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def delete_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)

    if request.method == "POST":
        # Delete the file from storage
        if document.file:
            document.file.delete(save=False)

        document.delete()
        messages.success(request, "Document deleted successfully!")
    else:
        messages.error(request, "Invalid request method.")

    return redirect("admin_dashboard")


# -------------------------
# Dashboard
# -------------------------
from django.shortcuts import render, redirect
from .models import Document, Department

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("user_login")

    user_role = "Unknown"
    user_department_name = None

    if hasattr(request.user, "engineer"):
        user_role = "Engineer"
        user_department_name = "Technical"
    elif hasattr(request.user, "operationsuser"):
        user_role = "Operations"
        user_department_name = "Operational"
    elif hasattr(request.user, "financeuser"):
        user_role = "Finance"
        user_department_name = "Financial"
    elif hasattr(request.user, "hruser"):
        user_role = "HR/Admin"
        user_department_name = "Administrative"
    elif hasattr(request.user, "complianceuser"):
        user_role = "Compliance"
        user_department_name = "Regulatory"
    elif hasattr(request.user, "executiveuser"):
        user_role = "Executive"
        user_department_name = "Executive"

    category_name = role_to_category.get(user_role)

    # Filter documents that have this category
    filtered_docs = Document.objects.filter(categories__name=category_name).distinct()


    return render(request, "dashboard.html", {
        "user": request.user,
        "role": user_role,
        "documents": filtered_docs,
    })


# -------------------------
# Logout
# -------------------------
def user_logout(request):
    logout(request)
    return redirect("home")

