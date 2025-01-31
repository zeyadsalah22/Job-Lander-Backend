from django.contrib import admin
from .models import Company, Employee, Application, Question, TodoList, CompanyQuestions

# Register your models here.
admin.site.register(Company)
admin.site.register(Employee)
admin.site.register(Application)
admin.site.register(Question)
admin.site.register(TodoList)
admin.site.register(CompanyQuestions)

