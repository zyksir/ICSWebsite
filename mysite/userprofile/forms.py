from django import forms
from django.contrib.auth.models import User
from .models import *

class PostForm(forms.ModelForm):
	
	text = forms.CharField(widget=forms.Textarea)
	
	class Meta:
		model = Post
		fields = ['text']

class CommentForm(forms.ModelForm):

	comment = forms.CharField(widget=forms.Textarea)

	class Meta:
		model = Comment
		fields = ['comment']

