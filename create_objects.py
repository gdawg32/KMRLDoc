# create_objects.py
import django
import os

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")
django.setup()

from home.models import Category, Department

# -------------------------
# Categories
# -------------------------
categories = [
    "Technical",
    "Operational",
    "Financial",
    "Administrative",
    "Regulatory",
    "Executive",
    "Mixed"
]

for cat in categories:
    obj, created = Category.objects.get_or_create(name=cat)
    if created:
        print(f"Category '{cat}' created.")
    else:
        print(f"Category '{cat}' already exists.")

# -------------------------
# Departments
# -------------------------
departments = [
    "Engineering",
    "Operations/Safety",
    "Finance/Procurement",
    "HR/Admin",
    "Compliance/Legal",
    "Executive/Management"
]

for dept in departments:
    obj, created = Department.objects.get_or_create(name=dept)
    if created:
        print(f"Department '{dept}' created.")
    else:
        print(f"Department '{dept}' already exists.")

print("Initial Categories and Departments setup completed.")
