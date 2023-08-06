from django.contrib import admin
from .models import Department, Teacher, Student, Paper, Question_answer

admin.site.register(Department)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Paper)
admin.site.register(Question_answer)
