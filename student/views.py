from django.shortcuts import render,redirect
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm



def student_login_view(request):
   
    form = AuthenticationForm()

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(username=username, password=password)

            if user is not None and user.groups.filter(name='STUDENT').exists():
                login(request, user)
                return redirect("student-dashboard")
            else:
                messages.error(request, "Invalid Student Username or Password")

    return render(request, "student/studentlogin.html", {"form": form})

#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return redirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm = forms.StudentUserForm()
    studentForm = forms.StudentForm()
    mydict = {'userForm': userForm, 'studentForm': studentForm}

    if request.method == 'POST':
        userForm = forms.StudentUserForm(request.POST)
        studentForm = forms.StudentForm(request.POST, request.FILES)

        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()

            student = studentForm.save(commit=False)
            student.user = user
            student.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

            return redirect('studentlogin')
        else:
            print(userForm.errors)
            print(studentForm.errors)

    return render(request, 'student/studentsignup.html', context=mydict)
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    student = models.Student.objects.get(user_id=request.user.id)
    result = QMODEL.Result.objects.filter(student=student).order_by('-id').first()

    total_course = QMODEL.Course.objects.count()
    total_question = QMODEL.Question.objects.count()

    return render(request, 'student/student_dashboard.html', {
        'student': student,
        'result': result,
        'total_course': total_course,
        'total_question': total_question,
    })

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    student = models.Student.objects.get(user_id=request.user.id)

    courses = QMODEL.Course.objects.all()

    attempted_courses = QMODEL.Result.objects.filter(
        student=student
    ).values_list('exam_id', flat=True)

    return render(request, 'student/student_exam.html', {
        'courses': courses,
        'attempted_courses': attempted_courses,
    })

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)

    # Student already attempted this exam
    already_attempted = QMODEL.Result.objects.filter(
        student=student,
        exam=course
    ).exists()

    if already_attempted:
        return render(request, 'student/already_attempted.html', {
            'course': course,
        })

    total_questions = QMODEL.Question.objects.filter(course=course).count()
    questions = QMODEL.Question.objects.filter(course=course)

    total_marks = 0
    for q in questions:
        total_marks += q.marks

    return render(request, 'student/take_exam.html', {
        'course': course,
        'total_questions': total_questions,
        'total_marks': total_marks
    })

@never_cache
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)

    student = models.Student.objects.get(user_id=request.user.id)

   
    if QMODEL.Result.objects.filter(student=student, exam=course).exists():
        return redirect('student-exam')

    questions = QMODEL.Question.objects.filter(course=course)

    response = render(request, 'student/start_exam.html', {
        'course': course,
        'questions': questions
    })
    response.set_cookie('course_id', course.id)
    return response


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course = QMODEL.Course.objects.get(id=course_id)

        total_marks = 0
        questions = QMODEL.Question.objects.filter(course=course)

        for i in range(len(questions)):
            selected_ans = request.COOKIES.get(str(i+1))
            actual_answer = questions[i].answer
            if selected_ans == actual_answer:
                total_marks += questions[i].marks

        student = models.Student.objects.get(user_id=request.user.id)

        result = QMODEL.Result()
        result.marks = total_marks
        result.exam = course
        result.student = student

        correct_answers = []

        for i in range(len(questions)):
            selected_ans = request.COOKIES.get(str(i+1))
            actual_answer = questions[i].answer

            correct_answers.append({
    'question': questions[i].question,
    'selected': getattr(questions[i], selected_ans.lower()) if selected_ans else "Not Answered",
    'correct': getattr(questions[i], actual_answer.lower()),
    'is_correct': selected_ans == actual_answer,
})
        result.save()

        return render(request, 'student/result.html', {
            'score': total_marks,
            'answers': correct_answers,
        })

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'student/check_marks.html',{'results':results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_marks.html',{'courses':courses})
  