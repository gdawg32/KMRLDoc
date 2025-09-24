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

    # Department origin (optional, human annotation)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    # File itself
    file = models.FileField(upload_to='documents/')

    # Language handling
    original_language = models.CharField(
        max_length=20,
        choices=[('en','English'), ('ml','Malayalam'), ('hybrid','Hybrid')]
    )
    detected_language = models.CharField(max_length=20, blank=True, null=True)  # auto-detected

    # Classification
    categories = models.ManyToManyField(Category, blank=True)  # multi-label from ML
    confidence_scores = models.JSONField(blank=True, null=True)  # {"Technical": 0.87, "Operational": 0.44, ...}

    # Extracted & processed content
    extracted_text = models.TextField(blank=True, null=True)   # raw OCR / text extraction
    translated_text = models.TextField(blank=True, null=True)  # English if translated
    summary = models.TextField(blank=True, null=True)          # LLM summarization

    # Tracking / status
    processed = models.BooleanField(default=False)             # whether ML pipeline ran
    last_processed = models.DateTimeField(blank=True, null=True)

    # Metadata
    metadata = models.JSONField(blank=True, null=True)         # {"pages": 12, "file_type": "pdf", ...}

    def __str__(self):
        return self.title


