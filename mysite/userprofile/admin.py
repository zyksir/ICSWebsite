from django.contrib import admin
from userprofile.models import *
# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_description', 'post', 'user' )

class PostAdmin(admin.ModelAdmin):
	list_display = ('short_description','id' ,'user', 'likes','like_flag')
	list_editable = ('likes', 'like_flag')

class LikeAdmin(admin.ModelAdmin):
    list_display = ('user','post')

class PersonAdmin(admin.ModelAdmin):
	list_display = ('user', 'person')

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Person, PersonAdmin)
