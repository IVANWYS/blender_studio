from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import inspect
import re

User = get_user_model()

CLASSSTYLE = {"class": "form-control"}


def changeStatus(form, status):
    TAG = inspect.stack()[1].function.split("_")[-1]
    VALID = {"class": "form-control is-valid"}
    INVALID = {"class": "form-control is-invalid"}

    if status is True:
        Status = form.fields[TAG].widget.attrs.update(VALID)
    else:
        Status = form.fields[TAG].widget.attrs.update(INVALID)
    print(Status)
    return Status


class RegistrationForm(forms.Form):
    username = forms.CharField(
        label='Username', widget=forms.TextInput(attrs=CLASSSTYLE), max_length=50)
    email = forms.CharField(
        label='Email', widget=forms.TextInput(attrs=CLASSSTYLE))
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput(attrs=CLASSSTYLE, render_value=True))
    password2 = forms.CharField(
        label='Password Confirmation', widget=forms.PasswordInput(attrs=CLASSSTYLE, render_value=True))

    username.widget.attrs.update({'placeholder': 'Enter the name :'})

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) < 5:
            changeStatus(self, False)
            raise ValidationError(
                "Your username must be at least 6 characters long.")
        elif len(username) > 50:
            changeStatus(self, False)
            raise ValidationError("Your username is too long.")
        else:
            if User.objects.filter(username=username).exists():
                changeStatus(self, False)
                raise ValidationError(f"User {username} already exists.")

        changeStatus(self, True)
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+[a-zA-Z]$)", email):
            if User.objects.filter(email=email).exists():
                changeStatus(self, False)
                raise ValidationError("Your email already exists.")
        else:
            changeStatus(self, False)
            raise ValidationError("Please enter a valid email.")

        changeStatus(self, True)
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if len(password1) < 6:
            changeStatus(self, False)
            raise ValidationError("Your password is too short.")
        elif len(password1) > 20:
            changeStatus(self, False)
            raise ValidationError("Your password is too long.")

        changeStatus(self, True)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            changeStatus(self, False)
            raise ValidationError("Password mismatch. Please enter again.")
        elif password1 == password2:
            changeStatus(self, True)

        return password2
