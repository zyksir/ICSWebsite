from django.conf.urls import url, include
from . import views

app_name = 'userprofile'

urlpatterns = [

    url(r'^$',views.profile, name='profile'),
	url(r'^feed/$',views.feed, name='feed'),
	url(r'^edit/post/(?P<post_id>[0-9]+)/$', views.edit_post, name='edit_post'),
	url(r'^delete/post/(?P<post_id>[0-9]+)/$', views.delete_post, name='delete_post'),
	url(r'^search_person/$', views.find_person, name='find_person'),
	url(r'^comment/(?P<post_id>[0-9]+)/$', views.comment, name='comment'),
	url(r'^like/(?P<post_id>[0-9]+)/$', views.like, name='like'),
	url(r'^unlike/(?P<post_id>[0-9]+)/$', views.unlike, name='unlike'),
	url(r'^edit/comment/(?P<comment_id>[0-9]+)/$', views.edit_comment, name='edit_comment'),
	url(r'^delete/comment/(?P<comment_id>[0-9]+)/$', views.delete_comment, name='delete_comment'),
	url(r'^search_person/follow/(?P<user_id>[0-9]+)/$', views.follow, name='follow'),
	url(r'^followers/unfollow/(?P<user_id>[0-9]+)/$', views.unfollow, name='unfollow'),
	url(r'^followers/$', views.followers, name='followers'),
	url(r'^following/$', views.following, name='following'),
	
]