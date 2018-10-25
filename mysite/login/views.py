from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse


# Create your views here..
def login_user(request):
	if request.method == "POST":
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('userprofile:feed'))
			else:
				return render(request, 'login/login.html', {'error_message': 'Your account has been disabled'})
		else:
			return render(request, 'login/login.html', {'error_message': 'invalid credentials'})
	else:
		return render(request, 'login/login.html', )


def register_user(request):
	form = UserForm(request.POST or None)
	if form.is_valid():
		user1 = form.save(commit=False)
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		user1.set_password(password)
		user1.save()
		user1 = authenticate(username=username, password=password)
		if user1 is not None:
			if user1.is_active:
				login(request, user1)
				return render(request, 'login/login.html')
	context = {"form": form,}
	return render(request, 'login/register.html', context)


def logout_user(request):
	logout(request)
	form = UserForm(request.POST or None)
	context = {
        "form": form,
    }
	return HttpResponseRedirect(reverse('login:log_in'))