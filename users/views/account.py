from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from users.forms import RegistrationForm
# from users.models import CheckLogin
User = get_user_model()
# Create your views here.


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('welcome')
        else:
            messages.error(request, 'Invalid credentials !')
            return redirect('login')
    else:
        return render(request, 'account/login.html')


def user_logout(request):
    if not request.user.is_authenticated:
        return redirect('welcome')
    else:
        # CheckLogin.objects.filter(
        #     user=request.user, session_key=request.session.session_key).delete()
        logout(request)
        messages.success(request, "You are logging out !")
        return redirect('welcome')


def user_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']
            user = User.objects.create_user(
                username=username, password=password, email=email)
            #account = Account.objects.create(user_id=user.id, gender="M")
            loginacc = authenticate(username=username, password=password)
            login(request, loginacc)
            return redirect('welcome')
    else:
        form = RegistrationForm()

    return render(request, 'account/register.html', {'form': form})
