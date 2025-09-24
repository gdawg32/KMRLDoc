from django.db import models
from django.contrib.auth.models import User

# -------------------------
# Categories
# -------------------------
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# -------------------------
# Departments (optional)
# -------------------------
class Department(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# -------------------------
# Role Models (1 per KMRL user type)
# -------------------------

class Engineer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username


class OperationsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shift = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username


class FinanceUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username


class HRUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username


class ComplianceUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    legal_license_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username


class ExecutiveUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username


# -------------------------
# Documents
# -------------------------
class Document(models.Model):
    title = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='documents/')
    original_language = models.CharField(max_length=20, choices=[('en','English'), ('ml','Malayalam'), ('hybrid','Hybrid')])
    categories = models.ManyToManyField(Category, blank=True)  # Multi-label
    extracted_text = models.TextField(blank=True, null=True)
    translated_text = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# -------------------------
# Notifications / Routing
# -------------------------
class DocumentNotification(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    # Linking to roles for role-based delivery
    engineer = models.ForeignKey(Engineer, on_delete=models.SET_NULL, null=True, blank=True)
    operations_user = models.ForeignKey(OperationsUser, on_delete=models.SET_NULL, null=True, blank=True)
    finance_user = models.ForeignKey(FinanceUser, on_delete=models.SET_NULL, null=True, blank=True)
    hr_user = models.ForeignKey(HRUser, on_delete=models.SET_NULL, null=True, blank=True)
    compliance_user = models.ForeignKey(ComplianceUser, on_delete=models.SET_NULL, null=True, blank=True)
    executive_user = models.ForeignKey(ExecutiveUser, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.document.title} notifications"


# -------------------------
# Optional: Named Entities (NER)
# -------------------------
class NamedEntity(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    entity_type = models.CharField(max_length=50)  # e.g., DATE, MONEY, LOCATION
    text = models.CharField(max_length=255)
    start_char = models.IntegerField()
    end_char = models.IntegerField()

    def __str__(self):
        return f"{self.text} ({self.entity_type})"
