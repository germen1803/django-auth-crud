from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import Create_Task_Form
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
  return render(request, 'home.html')


# Listar tareas segun usuario
@login_required # Decorador para proteger rutas, esto hace que para ejecutar la función se debe estar logueado
def tasks(request):
  task = Task.objects.filter(user=request.user, date_completed__isnull=True)
  return render(request, 'tasks.html', {
    'tasks': task
  })

# Listar tareas completadas
@login_required
def completed_tasks(request):
  task = Task.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
  return render(request, 'completed_tasks.html', {
      'tasks': task
  })

# Mostrar la tarea con detalles y opción de actualizar
@login_required
def task_detail(request, task_id):
  if request.method == 'GET':
    task = get_object_or_404(Task, pk=task_id)
    form = Create_Task_Form(instance=task)
    return render(request, 'task_detail.html', {
        'task': task,
        'form': form
    })
  else:
    try:
      task = get_object_or_404(Task, pk=task_id, user=request.user)
      form = Create_Task_Form(request.POST, instance=task)
      form.save()
      return redirect('tasks')
    except ValueError:
      return render(request, 'task_detail.html', {
          'task': task,
          'form': form
      })

# Completar tarea
@login_required
def complete_task(request, task_id):
  task = get_object_or_404(Task, pk=task_id, user=request.user)
  if request.method == 'POST':
    task.date_completed = timezone.now()
    task.save()
    return redirect('tasks')

# Borrar tarea
@login_required
def delete_task(request, task_id):
  task = get_object_or_404(Task, pk=task_id, user=request.user)
  if request.method == 'POST':
    task.delete()
    return redirect('tasks')

# Crear tarea
@login_required
def create_task(request):
  if request.method == 'GET':
    return render(request, 'create_task.html', {
        'form': Create_Task_Form
    })
  else:
    try:
      form = Create_Task_Form(request.POST)
      new_task = form.save(commit=False)
      new_task.user = request.user
      new_task.save()
      return redirect('tasks')
    except ValueError:
      return render(request, 'create_task.html', {
        'form': Create_Task_Form,
        'error': 'Please provide valid data'
      })

# Creación de cuenta, login y cerrar sesión
def signup(request):

  if request.method == 'GET':
    return render(request, 'signup.html', {
        'form': UserCreationForm
    })
  else:
    if (request.POST['password1'] == request.POST['password2']):
      try:
        user = User.objects.create_user(username=request.POST['username'],
                                        password=request.POST['password2'])
        user.save()
        login(request, user)
        return redirect('tasks')
      except IntegrityError:
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Username already exists'
        })
    return render(request, 'signup.html', {
        'form': UserCreationForm,
        'error': 'Password don\'t match'
    })

@login_required
def signout(request):
  logout(request)
  return redirect('home')

def signin(request):
  if request.method == 'GET':
    return render(request, 'signin.html', {
        'form': AuthenticationForm
    })
  else:
    user = authenticate(request, username=request.POST['username'],
                password=request.POST['password'])
    if user is None:
      return render(request, 'signin.html', {
          'form': AuthenticationForm,
          'error': 'Username or password is incorrect'
      })
    else:
      login(request, user)
      return redirect('tasks')

