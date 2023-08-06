from django.shortcuts import render, redirect
from django.db.models import F
from .forms import *
from .models import *
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from .decorators import *
import datetime
from django.utils import timezone
from django.core import serializers
import json


def homepage(request):
    return redirect('login')


@must_login
@allowed_users(allowed_roles=['teacher'])
def create_paper(request):
    if request.method == 'POST':
        formdata = PaperForm(request.POST)
        if formdata.is_valid():
            paper = formdata.save(commit=False)
            paper.dept = request.user.teacher.dept
            paper.paper_setter = request.user.teacher
            paper.save()
            return redirect('papers_and_questions')
    form = PaperForm()
    context = {'form': form}
    return render(request, 'create.html', context)


@must_login
@allowed_users(allowed_roles=['teacher'])
def create_question(request, pk):
    if request.method == 'POST':
        formdata = Question_answerForm(request.POST, request.FILES)
        if formdata.is_valid():
            print(request.POST)
            q = formdata.save(commit=False)
            paper = Paper.objects.get(id=pk)
            q.paper = paper
            q.save()
            formdata.save_m2m()

            return redirect('view_paper_questions', pk)
    form = Question_answerForm()
    context = {'form': form}
    return render(request, 'create.html', context)


@must_login
@allowed_users(allowed_roles=['teacher'])
def update_paper(request, pk):
    paper = Paper.objects.get(id=pk)

    if request.method == 'POST':
        if not paper.unlock_paper:
            formdata = PaperForm(request.POST, instance=paper)
        else:
            formdata = PaperForm_unlocked(request.POST, instance=paper)
        if formdata.is_valid():
            formdata.save()
            if paper.unlock_paper:
                m = Marks.objects.filter(paper=paper)
                for x in m:
                    x.modified_om = x.om/paper.fm*paper.modified_fm
                    x.save()

            return redirect('papers_and_questions')
    if not paper.unlock_paper:
        form = PaperForm(instance=paper)
    else:
        form = PaperForm_unlocked(instance=paper)
    context = {'form': form}
    return render(request, 'create.html', context)


@must_login
@allowed_users(allowed_roles=['teacher'])
def update_question(request, pk):
    q = Question_answer.objects.get(id=pk)
    if request.method == 'POST':
        if q.paper.unlock_paper:
            formdata = Question_answerForm_unlocked(request.POST, instance=q)
        else:
            formdata = Question_answerForm(
                request.POST, files=request.FILES, instance=q)
        if formdata.is_valid():
            formdata.save()
            if q.paper.unlock_paper:
                s = Student.objects.filter(dept=q.paper.dept)
                for x in s:
                    check_and_save_marks(x, q.paper)
            return redirect('view_paper_questions', q.paper.id)

    if q.paper.unlock_paper:
        form = Question_answerForm_unlocked(instance=q)
    else:
        form = Question_answerForm(instance=q)
    context = {'form': form}
    return render(request, 'create.html', context)


@must_login
@allowed_users(allowed_roles=['teacher'])
def delete_paper(request, pk):
    paper = Paper.objects.get(id=pk)

    if request.method == 'POST':
        paper.delete()
        return redirect('papers_and_questions')
    context = {'paper': paper}
    return render(request, 'delete_paper.html', context)


@must_login
@allowed_users(allowed_roles=['teacher'])
def delete_question(request, pk):
    q = Question_answer.objects.get(id=pk)

    if request.method == 'POST':
        q.delete()
        return redirect('view_paper_questions', q.paper.id)
    context = {'q': q}
    return render(request, 'delete_question.html', context)


@auth_check
def login_page(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.groups.all()[0].name == 'teacher':
                return redirect('teacher_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.info(request, 'Wrong Credentials')

    context = {}
    return render(request, 'login.html', context)


@must_login
def change_password(request):

    if request.method == 'POST':
        formdata = PasswordChangeForm(user=request.user, data=request.POST)
        if formdata.is_valid():
            formdata.save()
            update_session_auth_hash(request, formdata.user)
            group = None
            if formdata.user.groups.exists():
                group = request.user.groups.all()[0].name
                if group == 'teacher':
                    return redirect('teacher_dashboard')
                else:
                    return redirect('student_dashboard')
        else:
            messages.info(
                request, 'Invalid old or new password(s). Follow Instructions properly.')
            return redirect('change_password')

    form = PasswordChangeForm(user=request.user)
    context = {'form': form}
    return render(request, 'change_password.html', context)


@must_login
@allowed_users(allowed_roles=['teacher'])
def teacher_dashboard(request):
    context = {}
    return render(request, 'teacher_dashboard.html', context)


@must_login
@allowed_users(allowed_roles=['teacher'])
def papers_and_questions(request):
    papers = request.user.teacher.paper_set.all()
    context = {'papers': papers}
    return render(request, 'papers_and_questions.html', context)


@must_login
@allowed_users(allowed_roles=['teacher'])
def view_paper_questions(request, pk):
    paper = Paper.objects.get(id=pk)
    q = Question_answer.objects.filter(paper=paper)
    tmpJson = serializers.serialize("json", q)
    tmpObj = json.dumps(tmpJson)
    context = {'paper': paper, 'q': tmpObj}
    return render(request, 'view_paper_questions.html', context)


@must_login
@allowed_users(allowed_roles=['teacher'])
def view_question(request, pk):
    # pass
    q = Question_answer.objects.get(id=pk)
    context = {'q': q}
    return render(request, 'view_question.html', context)


@must_login
@allowed_users(allowed_roles=['teacher'])
def unlock_papers_and_marks(request):

    papers = request.user.teacher.paper_set.all()
    curr_time = timezone.now()
    for x in papers:
        if x.publishable or not x.unlock_paper:
            continue
        if x.exam_date + x.duration + x.grace_time < curr_time:
            x.publishable = True
            x.save()

    if request.method == 'POST':
        print(request.POST)
        d = dict(request.POST)
        del d['csrfmiddlewaretoken']

        for p, c in d.items():
            paper = Paper.objects.get(id=p)
            if c[0] == 'unlock_paper':
                paper.unlock_paper = True
                paper.exam_date = curr_time
            else:
                paper.publish_result = True
                paper.result_date = curr_time
            paper.save()
        return redirect('teacher_dashboard')
    context = {'papers': papers, 'curr_time': curr_time}
    return render(request, 'unlock_papers_and_marks.html', context)


@must_login
@allowed_users(allowed_roles=['teacher'])
def marks_for_teacher(request):
    papers = request.user.teacher.paper_set.all()
    if request.method == 'POST':
        papers = request.user.teacher.paper_set.all()

        p_id = request.POST['paper']
        paper1 = Paper.objects.get(id=p_id)
        marks = Marks.objects.filter(paper=paper1)

        context = {'papers': papers, 'marks': marks, 'paper': paper1}
        return render(request, 'marks_for_teacher.html', context)

    context = {'papers': papers}
    return render(request, 'marks_for_teacher.html', context)


@must_login
@allowed_users(allowed_roles=['student'])
def marks_for_student(request, pk):
    paper = Paper.objects.get(id=pk)
    m = Marks.objects.get(paper=paper, student=request.user.student)
    published_papers = Paper.objects.filter(
        dept=request.user.student.dept, publish_result=True)
    context = {'m': m, 'paper': paper, 'published_papers': published_papers}
    return render(request, 'marks_for_student.html', context)


@must_login
@allowed_users(allowed_roles=['student'])
def student_dashboard(request):
    papers = Paper.objects.filter(
        dept=request.user.student.dept, unlock_paper=True)

    unattended_papers = papers.exclude(
        exam_entry__student=request.user.student)

    attended_papers = papers.filter(exam_entry__student=request.user.student)

    missed_papers = []
    give_papers = []
    attended1_papers = []
    resume_papers = []
    curr_time = timezone.now()
    for x in unattended_papers:
        if x.exam_date + x.duration + x.grace_time < curr_time:
            missed_papers.append(x)
        else:
            give_papers.append(x)

    for x in attended_papers:
        e = Exam_entry.objects.get(paper=x, student=request.user.student)
        if x.exam_date + x.duration + x.grace_time < curr_time or e.submitted:
            attended1_papers.append(x)
        else:
            resume_papers.append(x)
    published_papers = Paper.objects.filter(
        dept=request.user.student.dept, publish_result=True)

    no_paper=not(missed_papers or give_papers or resume_papers or attended1_papers or published_papers)
    context = {
        'missed_papers': missed_papers,
        'give_papers': give_papers,
        'resume_papers': resume_papers,
        'attended_papers': attended1_papers,
        'published_papers': published_papers,
        'no_paper': no_paper,
    }
    return render(request, 'student_dashboard.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')


@must_login
@allowed_users(allowed_roles=['student'])
def give_exam(request, pk, type1):
    paper = Paper.objects.get(id=pk)
    student = request.user.student
    if request.method == 'POST':
        print(request.POST)
        if paper.exam_date + paper.duration + paper.grace_time >= timezone.now():
            Student_answer.objects.filter(
                student=student, question__paper=paper).delete()
            e = Exam_entry.objects.get(student=student, paper=paper)
            save_answer_ajax(student, e, dict(request.POST))
            e.submitted = True
            e.save()
        check_and_save_marks(student, paper)
        return redirect('student_dashboard')

    if type1 == 'n':
        if Exam_entry.objects.filter(student=student, paper=paper).count() > 0:
            e = Exam_entry.objects.get(
                paper=paper, student=student)
            if not (paper.exam_date + paper.duration + paper.grace_time < timezone.now() or not paper.unlock_paper or e.submitted):
                return redirect('give_exam', pk, 'r')
            else:
                return redirect('student_dashboard')
        n = paper.count
        arr1 = Question_answer.objects.filter(paper=paper)
        arr2 = arr1.random(n)

        timer_left_time = paper.duration    # time the stu currently has from the alloted exam duration

        e1 = Exam_entry(student=student, paper=paper,
                        time_left=timer_left_time)
        e1.save()
        e2 = Exam_entry.objects.get(student=student, paper=paper)
        for x in arr2:
            e2.question.add(x)
        e3 = e2

        temp_arr = serializers.serialize('json', arr2)
        arr_json = json.dumps(temp_arr)
        context = {'arr': arr_json, 'attempted_answers': None, 'arrL': n,
                   'timer_left_time': timer_left_time.seconds}

    else:
        e = Exam_entry.objects.get(paper=paper, student=request.user.student)
        if paper.exam_date + paper.duration + paper.grace_time < timezone.now() or not paper.unlock_paper or e.submitted:
            return redirect('student_dashboard')
        e = Exam_entry.objects.get(student=student, paper=paper)
        arr2 = e.question.all()
        attempted_answers = Student_answer.objects.filter(
            student=student, question__in=arr2)
        temp_arr = serializers.serialize('json', arr2)
        arr_json = json.dumps(temp_arr)
        temp_attempted_answers = serializers.serialize(
            'json', attempted_answers)
        attempted_answers_json = json.dumps(temp_attempted_answers)
        context = {'arr': arr_json, 'attempted_answers': attempted_answers_json, 'arrL': arr2.count(),
                   'timer_left_time': e.time_left.seconds}
        e3 = e
    total_time = paper.exam_date + paper.duration + paper.grace_time
    server_left_time = total_time-timezone.now()    # time left in the ongoing exam window
    context['server_left_time'] = server_left_time.seconds
    context['paper'] = paper
    context['warning'] = e3.warning

    return render(request, 'ajax_exam.html', context)


@must_login
@allowed_users(allowed_roles=['student'])
def ajax_exam(request, pk):
    if request.method == 'POST':
        print(request.POST)
        paper = Paper.objects.get(id=pk)
        if paper.exam_date + paper.duration + paper.grace_time >= timezone.now():
            student = request.user.student
            e = Exam_entry.objects.get(student=student, paper=paper)

            save_answer_ajax(student, e, dict(request.POST))
        return JsonResponse({'status': 1})


def check_and_save_marks(student, paper):
    ans = Student_answer.objects.filter(student=student, question__paper=paper)
    count = ans.count()

    correct_count = ans.filter(
        question__correct_option__iexact=F('selected_option')).count()

    wrong_count = count-correct_count
    om = correct_count*(paper.marks_per_cq)+wrong_count*(paper.marks_per_wq)

    modified_om = om/(paper.fm)*(paper.modified_fm)

    p = om/(paper.fm)*100
    if p >= 90:
        grade = 'A'
    elif p >= 80:
        grade = 'B'
    elif p >= 70:
        grade = 'C'
    elif p >= 60:
        grade = 'D'
    elif p >= 50:
        grade = 'E'
    else:
        grade = 'F'
    marks = Marks.objects.filter(student=student, paper=paper)
    if marks.count() == 0:
        mark = Marks(student=student, paper=paper, om=om,
                     modified_om=modified_om, grade=grade)
        mark.save()
    else:
        m = marks[0]
        m.om = om
        m.modified_om = modified_om
        m.grade = grade
        m.save()


def save_answer_ajax(student, e, d1):
    del d1['csrfmiddlewaretoken']
    for q, a in d1.items():
        if len(a[0]) == 0:
            continue
        if q == 'timer_left_time':
            e.time_left = datetime.timedelta(seconds=int(a[0]))
            e.save()
            continue
        if q == 'warning':
            e.warning = int(a[0])
            e.save()
            continue

        temp1 = student.student_answer_set.filter(question__id=q)
        if temp1:
            if temp1[0].selected_option == a[0]:
                pass
            elif a[0] == 'u':
                temp1[0].delete()
            else:
                temp1[0].selected_option = a[0]
                temp1[0].save()
        else:
            if a[0] == 'u':
                pass
            else:
                question = Question_answer.objects.get(id=q)
                selected_option = a[0]
                s_a_temp = Student_answer(
                    student=student, question=question, selected_option=selected_option)
                s_a_temp.save()
