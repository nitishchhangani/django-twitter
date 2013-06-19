import re
from django import forms
from django.contrib.auth.models import User
from twitter import models


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ['dob', 'interests']


class TweetForm(forms.ModelForm):
    class Meta:
        model = models.Tweet
        fields = ['group', 'message']

    def save(self, user):
        tweet = super(TweetForm, self).save(commit=False)
        tweet.user=user
        tweet.save()
        return tweet


class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    repassword = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("User already exists!")
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        if not re.search('\d', password) or not re.search('([a-zA-Z][^a-zA-Z]*){5}',password):
            raise forms.ValidationError("Password should have atleast 5 letters and 1 number.")
        return password

    def clean_repassword(self):
        password = self.cleaned_data['password']
        repassword = self.cleaned_data['repassword']
        if password != repassword:
            raise forms.ValidationError("Passwords don't match.")
        return repassword

    def save(self):
        password = self.clean_password()
        user = super(SignupForm, self).save(commit=False)
        user.set_password(password)
        user.save()
        return user