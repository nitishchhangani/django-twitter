from django.conf.urls import patterns, url
from twitter import views
from twitter.decorators import logout_required
from django.contrib.auth.views import login

urlpatterns = patterns('',
    url(r'^$', logout_required(login), {'template_name': 'twitter/login_form.html'}, name='login'),
    url(r'^home/$', views.Home.as_view(), name='home'),
    url(r'^(?P<user>\w+)/profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^(?P<user>\w+)/edit/$', views.EditProfileView.as_view(), name='edit'),
    url(r'^logout/$', views.Logout.as_view(), name='logout'),
    url(r'^signup/$', logout_required(views.Signup.as_view()), name='signup'),
    url(r'^add/tweet/$', views.AddTweet.as_view(), name='addtweet'),
    url(r'^(?P<user>\w+)/tweets/$', views.ViewTweet.as_view(), name='viewtweet'),
    url(r'^connect/$', views.ConnectView.as_view(), name='connect'),
    url(r'^connectto/(?P<user>\w+)/$', views.ConnectToView.as_view(), name='connectto'),
    url(r'^confirm/(?P<confirm_code>[^/]+)/$', views.ConfirmView.as_view(), name='confirm'),
    url(r'^reject/(?P<confirm_code>[^/]+)/$', views.RejectView.as_view(), name='reject'),
    url(r'^disconnectfrom/(?P<user>\w+)/$', views.DisconnectFromView.as_view(), name='disconnectfrom'),
)