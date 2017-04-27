from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse

from . import views, rest_views

urlpatterns = [
	url(r'^updatenumberofattending/$', rest_views.updatenumberofattending, name='updatenumberofattending'),
	url(r'^eventinformation/$', rest_views.eventinformation, name='eventinformation'),
	url(r'^getusernamebyid/$', rest_views.getusernamebyid, name='getusernamebyid'),
	url(r'^geteventusername/$', rest_views.geteventusername, name='geteventusername'),
	url(r'^displayevents/$', rest_views.displayevents, name='displayevents'),
	url(r'^addeventtomap/$', rest_views.addeventtomap, name='addeventtomap'),
	url(r'^listfriends/$', rest_views.listfriends, name='listfriends'),
	url(r'^addfriend/$', rest_views.addfriend, name='addfriend'),
	url(r'^searchuser/$', rest_views.getUserPosition.as_view(), name='searchuser'),
	url(r'^getgroups/$', rest_views.token_getGroups, name='token_getgroups'),
	url(r'^addgroup/$', rest_views.token_addgroup, name='token_addgroup'),
	url(r'^signup/$', rest_views.token_signup, name='token-signup'),
    url(r'^tokenlogin/$', rest_views.token_login, name='token-login'),
    url(r'^userme/$', rest_views.UserMe_R.as_view(), name='user-me'),
    url(r'^users/$', rest_views.UsersList.as_view(), name='users'),
    url(r'^user/(?P<email>[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)/$', rest_views.UserOther_R.as_view(), name='user-email'),
    url(r'^user/(?P<uid>\d+)/$', rest_views.UserOther_R.as_view(), name='user-username'),
    url(r'^updateposition/$', rest_views.UpdatePosition.as_view(), name='update-position'),
]
