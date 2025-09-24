from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Department)
admin.site.register(Category)
admin.site.register(Engineer)
admin.site.register(OperationsUser)
admin.site.register(FinanceUser)
admin.site.register(HRUser)
admin.site.register(ComplianceUser)
admin.site.register(ExecutiveUser)
admin.site.register(Document) 