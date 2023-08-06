from django.db import models
from django.contrib.auth.models import User
from django_random_queryset import RandomManager


class Department(models.Model):
    ID = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    ID = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=50)
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
    post = models.CharField(max_length=20)
    dept = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Student(models.Model):
    ID = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=50)
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
    roll = models.IntegerField()
    sem = models.IntegerField()
    academic_year = models.IntegerField()
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Paper(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=20)
    count = models.IntegerField()
    marks_per_cq = models.IntegerField()
    marks_per_wq = models.FloatField()
    fm = models.IntegerField()
    modified_fm = models.FloatField()
    duration = models.DurationField(null=True, blank=True)
    grace_time = models.DurationField(null=True, blank=True)
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    paper_setter = models.ForeignKey(
        Teacher, null=True, on_delete=models.SET_NULL)
    unlock_paper = models.BooleanField(default=False)
    publishable = models.BooleanField(default=False)
    publish_result = models.BooleanField(default=False)
    exam_date = models.DateTimeField(null=True)
    result_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.name


class Question_answer(models.Model):
    objects = RandomManager()
    options = [
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D')
    ]
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    desc = models.TextField(max_length=100)
    op1 = models.CharField(max_length=50)
    op2 = models.CharField(max_length=50)
    op3 = models.CharField(max_length=50)
    op4 = models.CharField(max_length=50)

    correct_option = models.CharField(choices=options, max_length=1)
    img_path = models.ImageField(
        blank=True, null=True, upload_to='exam_images')

    def __str__(self):
        return self.desc[:10]


class Student_answer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question_answer, null=True, on_delete=models.SET_NULL)
    selected_option = models.CharField(max_length=1)

    def __str__(self):
        return self.selected_option


class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    om = models.FloatField()
    modified_om = models.FloatField()
    grade = models.CharField(max_length=10)

    def __str__(self):
        return str(self.modified_om)


class Exam_entry(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    time_left = models.DurationField(null=True, blank=True)
    submitted = models.BooleanField(default=False)
    question = models.ManyToManyField(Question_answer)
    warning = models.IntegerField(default=20)
