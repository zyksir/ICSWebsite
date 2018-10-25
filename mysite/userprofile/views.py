from django.shortcuts import render
from userprofile.models import *
from userprofile.forms import *
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
import simplejson as json
# Create your views here...

def posts_in_feed(request):
	user = request.user
	persons = Person.objects.filter(user=user)
	posts = []
	for person in persons:
			for p in Post.objects.filter(user=person.person):
				posts.append(p)

	for p in Post.objects.filter(user=user):
		posts.append(p)

	return posts

# def comments_in_feed():
# 	comments = Comment.objects.all()
# 	return comments

def profile(request):
	if not request.user.is_authenticated:
		return render(request, 'login/login.html')

	else:
		#display recent posts
		user = request.user
		posts = Post.objects.filter(user=request.user)

		#to create a new post
		form = PostForm(request.POST or None)
		if form.is_valid():
			post = form.save(commit=False)
			post.user = request.user
			post.save()

		return render(request, 'profile.html',{'posts':posts,'user':user, 'form':form})

def feed(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login:log_in'))

	else:
		user = request.user
		user_likes = Like.objects.filter(user=user)
		
		#setting all the like_flags to false for all the posts
		Post.objects.all().update(like_flag=False)
		
		#setting like_flags to true for the posts that user has already liked
		for l in user_likes:
			post = Post.objects.get(id=l.post_id)
			post.like_flag = True
			post.save()

		posts = posts_in_feed(request)
		posts = sorted(posts, key = lambda x: x.published_on, reverse=True)
		
		#pagination
		paginator = Paginator(posts, 4)
		try:
			page_posts = paginator.page(request.GET.get('page'))

		except PageNotAnInteger:
			page_posts = paginator.page(1)

		except EmptyPage:
			page_posts = paginator.page(paginator.num_pages)
			
		return render(request, 'home.html',{'posts':page_posts,'user':user})


def edit_post(request, post_id):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login:log_in'))

	else:
		post_object = Post.objects.get(id=post_id)
		posts = Post.objects.filter(user=request.user)
		user = request.user
		text = post_object.text
		form = PostForm()
		
		if user == post_object.user:
			if request.method == 'POST':
				post_object.text = request.POST.get('posttext')
				post_object.save()
				return HttpResponseRedirect(reverse('userprofile:profile'))
		else:
			return HttpResponse('You are not authorized for this action')
		return render(request, 'edit_post.html',{'post':text})

def delete_post(request, post_id):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login:log_in'))

	else:
		instance = Post.objects.get(id=post_id)
		posts = Post.objects.filter(user=request.user)
		user = request.user
		if instance.user == user:
			instance.delete()
			return HttpResponseRedirect(reverse('userprofile:profile'))
		return HttpResponse('You are not authorized for this action')

def find_person(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login:log_in'))

	else:
		if request.method == 'GET':
			q = request.GET.get('search_box')
			persons = User.objects.filter(username__icontains=q)
			return render(request, 'search.html',{'query':q,'results':persons, 'user':request.user})
		return HttpResponseRedirect(reverse('userprofile:feed'))

def like(request, post_id):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login:log_in'))

	else:
		if request.is_ajax:
			post = Post.objects.get(id=post_id)
			new_like = None
			new_like, created= Like.objects.get_or_create(user=request.user, post=post)
			if created:
				post.likes += 1
				post.like_flag = True
				post.save()
				resp = {}
				resp['likes'] = post.likes
				return HttpResponse(json.dumps(resp), content_type='application/json')
			


def unlike(request, post_id):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login:log_in'))

	else:
		if request.is_ajax:
			user = request.user
			post = Post.objects.get(id=post_id)
			
			unlike = None
			unlike = Like.objects.get(user=user, post=post)
			if unlike!=None:
				post.likes = post.likes - 1
				post.like_flag = False
				post.save()
				unlike.delete()
				post = Post.objects.get(id=post_id)
				resp = {}
				resp['likes'] = post.likes
				return HttpResponse(json.dumps(resp), content_type='application/json')

def comment(request, post_id):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login:log_in'))

	else:
		# ---- static comment logic ----

		# posts = posts_in_feed(request)
		# user = request.user
		# form = CommentForm(request.POST or None)
		# if form.is_valid():
		# 	comment = form.save(commit=False)
		# 	comment.user = user
		# 	comment.post = Post.objects.get(id=post_id)
		# 	comment.save()
		# 	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		# return HttpResponseRedirect(reverse('userprofile:feed'))


		# adding comments with AJAX
		posts = posts_in_feed(request)
		if request.method == 'POST':
			if request.is_ajax:
				user = request.user
				comment = Comment(comment = request.POST.get('comment'), user=user, post=Post.objects.get(id=post_id))
				comment.save()
				response_data ={}
				response_data['comment'] = comment.comment
				response_data['user'] = str(comment.user)
				response_data['published_on'] = comment.published_on.strftime('%B %d, %Y %I:%M %p')
				response_data['c_id'] = comment.id
				return HttpResponse(json.dumps(response_data),content_type="application/json")


def edit_comment(request, comment_id):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login:log_in'))

	else:
		comment = Comment.objects.get(id=comment_id)

		if request.user == comment.user:
			
			if request.is_ajax:
				if request.method == 'POST':
					comment.comment = request.POST.get('comment')
					comment.save()
					response_data = {}
					response_data['comment'] = comment.comment
					response_data['user'] = str(comment.user)
					response_data['published_on'] = str(comment.published_on)
					return HttpResponse(json.dumps(response_data), content_type='application/json')
		else:
			return HttpResponse("You are not authorized for this action!")



def delete_comment(request, comment_id):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login:log_in'))

	else:
		comment = Comment.objects.get(id=comment_id)

		if request.user == comment.user:
			if request.is_ajax:
				comment.delete()
				# resp = {}
				# resp['message'] = 'deleted!!'
				return HttpResponse()
		else:
			return HttpResponse("You are not authorized for this action!")


def follow(request, user_id):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login:log_in'))

	else:	
		other_user = User.objects.get(id=user_id)
		if not request.user == other_user:
			person, created = Person.objects.get_or_create(user=request.user, person=other_user)
			if not created:
				return HttpResponse("You are following this person already!!")
			else:
				return HttpResponseRedirect(reverse('userprofile:feed'))
		else:
			return HttpResponse("You following youself already!!")


def unfollow(request, user_id):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login:log_in'))

	else:
		
		person = Person.objects.get(id=user_id)
		if request.user == person.user:
			person.delete()
			return HttpResponseRedirect(reverse('userprofile:feed'))
		else:
			return HttpResponse("You are not authorized for this action!")


def following(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login:log_in'))

	else:
		persons = Person.objects.filter(user=request.user)
		return render(request, 'following.html',{'persons':persons})


def followers(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(reverse('login:log_in'))

	else:
		user = request.user
		persons = Person.objects.filter(person=user)
		return render(request, 'followers.html',{'persons':persons})
