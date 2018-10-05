from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import get_user_model, authenticate, login, logout
from .forms import RegisterForm, LoginForm

User=get_user_model() 

def index(request):
	context={
		"hi":"hello"
	}
	return render(request, "index.html", context)
	# return HttpResponse("HELLo")

def home_page(request):
	context = {
		'title':request.user.username
	}
	return render(request,"home_page.html",context)
	#return HttpResponse("<h1>Hello World</h1>")

def contact(request):
	if request.method == "POST":

		fullname = request.POST.get('fullname')
		number   = request.POST.get('contact')
		address  = request.POST.get('address')
		print(fullname,number,address)
	return render(request,"contact.html")

def login_user(request):

	if request.user.is_authenticated:
		return HttpResponseRedirect("/home/")
	else:
		# form=LoginForm(request.POST or None)

		# context={
		# 	"message":"LOG-IN",
		# 	"form":form
		# }

		# if form.is_valid():
		# 	username=form.cleaned_data.get("username")
		# 	password=form.cleaned_data.get("password")

		# 	user=authenticate(request, username=username, password=password)
		# 	print(user)

		# 	if user is not None:
		# 		login(request, user)
		# 		return HttpResponseRedirect("/home/")
		# 	else:
		# 		print("There is an error in your login information")

		context={
			"message":"LOG-IN",
		}

		if request.method == "POST":
			print("Log In Will Be")
			username=request.POST.get('username')
			password=request.POST.get('password')

			print(username)
			print(password)

			user=authenticate(request, username=username, password=password)
			print(user)

			if user is not None:
				login(request, user)
				return HttpResponseRedirect("/home/")
			else:
				print("There is an error in your login information")


		return render(request, "login.html", context)


def signup_user(request):

	if request.user.is_authenticated:
		print("Auth")

		return HttpResponseRedirect("/home/")

	else:
		# print("Not Auth")

		# form=RegisterForm(request.POST or None)

		# context = {
		# 	"message":"SIGN-UP",
		# 	"form":form
		# }

		# if form.is_valid():		
		# 	# print(form.cleaned_data)

		# 	username=form.cleaned_data.get("username")
		# 	email=form.cleaned_data.get("email")
		# 	password=form.cleaned_data.get("password")

		# 	new_user = User.objects.create_user(username, email, password)
		# 	user=authenticate(request, username=username, password=password)
		# 	login(request, user)

		# 	return HttpResponseRedirect("/home/")

		context={
			"message":"LOG-IN",
		}

		if request.method == "POST":
			print("Log In Will Be")
			username=request.POST.get('username')
			email=request.POST.get('email')
			password=request.POST.get('password')

			print(username)
			print(password)
			print(email)

			user=User()
			user.username=username
			user.email=email
			user.password=password
			user.save()

			# user=authenticate(request, username=username, password=password)
			# print(user)

			login(request, user)
			return HttpResponseRedirect("/home/")

			# if user is not None:
			# 	login(request, user)
			# 	return HttpResponseRedirect("/home/")
			# else:
			# 	print("There is an error in your login information")

		return render(request, "signup.html", context)

def logout_user(request):
	logout(request)
	return HttpResponseRedirect("/")
