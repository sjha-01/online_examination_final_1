from django.http import HttpResponse
from django.shortcuts import redirect


def auth_check(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                if group == 'teacher':
                    return redirect('teacher_dashboard')
                else:
                    return redirect('student_dashboard')

        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func
    
def must_login(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('You are not allowed here.')
        return wrapper_func
    return decorator
