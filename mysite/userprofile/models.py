from django.db import models
from django.contrib.auth.models import Permission, User
from django.template.defaultfilters import truncatechars
# Create your models here.
class Post(models.Model):

	user = models.ForeignKey(User,on_delete=models.CASCADE)
	text = models.CharField(max_length=1000)
	published_on = models.DateTimeField(auto_now_add=True)
	likes = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
	like_flag = models.NullBooleanField(default=False)
	class Meta:
		ordering = ['-published_on']

	@property
	def short_description(self):
		return truncatechars(self.text, 35)

	def __str__(self):
		return truncatechars(self.text, 35)


class Comment(models.Model):

	user = models.ForeignKey(User,on_delete=models.CASCADE)
	post = models.ForeignKey(Post,on_delete=models.CASCADE)
	comment = models.CharField(max_length=1000)
	published_on = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-published_on']

	@property
	def short_description(self):
		return truncatechars(self.comment, 35)

	def __str__(self):
		return truncatechars(self.comment, 35)

class Like(models.Model):

	user = models.ForeignKey(User,on_delete=models.CASCADE)
	post = models.ForeignKey(Post,on_delete=models.CASCADE)
	published_on = models.DateTimeField(auto_now=True)

class Person(models.Model):
	
	user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
	person = models.ForeignKey(User, related_name='people', on_delete=models.CASCADE, null=True)
	followed_on = models.DateTimeField(auto_now_add=True)