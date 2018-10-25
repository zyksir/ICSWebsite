from django.conf.urls import url, include
from . import views

app_name = 'login'

urlpatterns = [
    
    url(r'^login/',views.login_user, name='log_in'),
    url(r'^$',views.login_user),
    url(r'^register/$',views.register_user, name='register'),
	url(r'^logout/$',views.logout_user, name='logout_user'),

]