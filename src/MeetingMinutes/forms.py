from django import forms
from django.contrib.auth import get_user_model

User=get_user_model()

class RegisterForm(forms.Form):
	username=forms.CharField()
	email=forms.EmailField()
	password=forms.CharField(widget=forms.PasswordInput)

	def clean_username(self):
		username=self.cleaned_data.get('username')
		qs=User.objects.filter(username=username)
		if qs.exists():
			raise forms.ValidationError("Username is already taken")
		return username

	def clean_email(self):
		email=self.cleaned_data.get('email')
		qs=User.objects.filter(email=email)
		if qs.exists():
			raise forms.ValidationError('A User with this email already exists')
		return email

class LoginForm(forms.Form):
	username=forms.CharField()
	password=forms.CharField(widget=forms.PasswordInput)

	def clean_info(self):
		username=self.cleaned_data.get('username')
		password=self.cleaned_data.get('password')
		qs=User.objects.filter(username=username, password=password)
		if not qs.exists():
			raise forms.ValidationError('There is an error in your information')
		return password
