import random
import re
import string
from django.core.mail import send_mail
from django.db.models import Q, Count
from django.http import HttpResponseRedirect
from django.views import generic
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.contrib.auth.models import User
from twitter.forms import *
from twitter.models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings


class ProfileView(generic.View):
    http_method_names = ['dispatch', 'get']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileView, self).dispatch( *args, **kwargs)

    def get(self, request, user, *args, **kwargs):
        user = User.objects.get(username=user)
        profile, created = Profile.objects.get_or_create(user=user)
        user_list = User.objects.all()
        return render(request, 'twitter/profile.html', {
            'user': user,
            'profile': profile,
            'user_list': user_list,
            'current_user': request.user
        })


class EditProfileView(generic.View):
    http_method_names = ['dispatch', 'get', 'post']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EditProfileView, self).dispatch(*args, **kwargs)

    def get(self, request, user, *args, **kwargs):
        user = User.objects.get(username=user)
        if not user == request.user:
            return HttpResponseRedirect(reverse('profile', args=(user,)))
        profile, created = Profile.objects.get_or_create(user=user)
        profile_form = ProfileForm(instance=profile)
        user_form = UserForm(instance=user)
        return render(request, 'twitter/edit.html', {
            'user': user,
            'profile_form': profile_form,
            'user_form': user_form,
            'current_user': request.user
        })

    def post(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.get(user=user)
        profile_form = ProfileForm(request.POST,instance=profile)
        user_form = UserForm(request.POST,instance=user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse('profile', args=(user,)))
        return render(request, 'twitter/edit.html', {
            'user': user,
            'profile_form': profile_form,
            'user_form': user_form,
            'current_user': request.user
        })


class Home(generic.View):
    http_method_names = ['dispatch', 'get']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Home, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        notification_list = Notify.objects.filter(user1=request.user)
        return render(request, 'twitter/home.html', {
            'user': request.user,
            'notification_list': notification_list
        })


class ViewTweet(generic.View):
    http_method_names = ['dispatch', 'get']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ViewTweet, self).dispatch(*args, **kwargs)

    def get(self, request, user, *args, **kwargs):
        user = User.objects.get(username=user)
        tweets = Tweet.objects.filter(user=user)
        current_user = request.user
        list_user = [current_user, user]
        if current_user == user:
            tweet_list = tweets
        elif Connect.objects.filter(user1__in=list_user, user2__in=list_user, is_active=True).exists():
            tweet_list = list()
            for tweet in tweets:
                if tweet.group != tweet.private:
                    tweet_list.append(tweet)
        else:
            tweet_list = list()
            for tweet in tweets:
                if tweet.group == tweet.public:
                    tweet_list.append(tweet)

        user_list = User.objects.all()
        return render(request, 'twitter/view_tweet.html', {
            'user_list': user_list,
            'tweet_list': tweet_list,
        })


class ConnectView(generic.View):
    http_method_names = ['dispatch', 'get']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ConnectView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        exclude_list = list()
        exclude_list.append(request.user.username)
        connected_users = Connect.objects.filter(Q(user1=request.user) | Q(user2=request.user))
        connected_list = list()
        pending_list = list()
        accept_list = list()
        for users in connected_users:
            if users.user1 == request.user:
                if users.is_active:
                    connected_list.append(users.user2)
                else:
                    pending_list.append(users.user2)
                exclude_list.append(users.user2.username)
            elif users.user2 == request.user:
                if users.is_active:
                    connected_list.append(users.user1)
                else:
                    accept_list.append(users.user1)
                exclude_list.append(users.user1.username)

        reject_list = Reject.objects.filter(user2=request.user).values('user1__username').annotate(Count('user1'))
        reject_list = reject_list.filter(user1__count__gte=settings.MAX_REJECT_COUNT)
        for reject in reject_list:
            exclude_list.append(reject['user1__username'])
        disconnected_list = User.objects.exclude(username__in=exclude_list)
        return render(request, 'twitter/connect.html', {
            'connected_list': connected_list,
            'disconnected_list': disconnected_list,
            'pending_list': pending_list,
            'accept_list': accept_list,
        })


class ConfirmView(generic.View):
    http_method_names = ['dispatch', 'get']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ConfirmView, self).dispatch(*args, **kwargs)

    def get(self, request, confirm_code, *args, **kwargs):
        connect = Connect.objects.filter(confirmation_code=confirm_code)
        if connect.exists():
            row = connect.get(confirmation_code=confirm_code)
            if request.user != row.user2:
                message = 'Permission denied.'
            else:
                if not row.is_active:
                    row.is_active = True
                    row.save()
                    message = ''.join([row.user1.username, ' is now connected to ', row.user2.username])
                else:
                    message = ''.join([row.user1.username, ' is already connected to ', row.user2.username])
        else:
            message = 'Invalid confirmation code.'
        return render(request, 'twitter/confirm_reject.html', {
            'message': message,
        })


class ConnectToView(generic.View):
    http_method_names = ['dispatch', 'get']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ConnectToView, self).dispatch(*args, **kwargs)

    def get(self, request, user, *args, **kwargs):
        current_user = request.user
        if current_user.username != user:
            connect_to = User.objects.get(username=user)
            list_user = [current_user, connect_to]
            if not Connect.objects.filter(user1__in=list_user, user2__in=list_user).exists():
                if not Reject.objects.filter(user1=connect_to,user2=current_user).count() >= 5:
                    confirmation_code = self.code_generator()
                    Connect.objects.create(user1=current_user,user2=connect_to, confirmation_code=confirmation_code)
                    subject = current_user.username + ' wants to connect to you'
                    message = ''.join(['Click to confirm: http://127.0.0.1:8000/twitter/confirm/', confirmation_code, '/\n'])
                    message = ''.join([message, 'Click to reject: http://127.0.0.1:8000/twitter/reject/', confirmation_code, '/'])
                    send_mail(subject, message, 'twitter@project.com',[connect_to.email], fail_silently=False)
        return HttpResponseRedirect(reverse('connect'))

    def code_generator(self, size=50, chars=string.ascii_letters+string.digits):
        return ''.join(random.choice(chars) for x in range(size))


class DisconnectFromView(generic.View):
    http_method_names = ['dispatch', 'get']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DisconnectFromView, self).dispatch(*args, **kwargs)

    def get(self, request, user, *args, **kwargs):
        if user != request.user.username:
            current_user = request.user
            disconnect_from = User.objects.get(username=user)
            list_user = [current_user, disconnect_from]
            Connect.objects.filter(user1__in=list_user, user2__in=list_user).delete()
        return HttpResponseRedirect(reverse('connect'))


class RejectView(generic.View):
    http_method_names = ['dispatch', 'get']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RejectView, self).dispatch(*args, **kwargs)

    def get(self, request, confirm_code, *args, **kwargs):
        connect = Connect.objects.filter(confirmation_code=confirm_code)
        if connect.exists():
            row = connect.get(confirmation_code=confirm_code)
            if request.user != row.user2:
                message = 'Permission denied.'
            else:
                if not row.is_active:
                    row.delete()
                    Reject.objects.create(user1=row.user2,user2=row.user1)
                    message = 'Request rejected successfully.'
                else:
                    message = 'Invalid rejection code.'
        else:
            message = 'Invalid rejection code.'
        return render(request, 'twitter/confirm_reject.html', {
            'message': message,
        })


class AddTweet(generic.View):
    http_method_names = ['dispatch', 'get', 'post']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AddTweet, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        tweetForm = TweetForm()
        return render(request, 'twitter/add_tweet.html', {
            'form': tweetForm,
        })

    def post(self, request, *args, **kwargs):
        user = request.user
        tweetForm = TweetForm(request.POST)
        if tweetForm.is_valid():
            tweet = tweetForm.save(user)
            message = tweet.message
            group = tweet.group
            if group != Tweet.private:
                user_list = re.findall('@(\w+)', message)
                if user.username in user_list:
                    user_list.remove(user.username)
                if user_list:
                    actual_users = User.objects.filter(username__in=user_list)
                    if actual_users.exists():
                        if group == Tweet.friends:
                            notify_users = list()
                            all_connected = Connect.objects.filter(Q(user1=user) | Q(user2=user), is_active=True)
                            for connected in all_connected:
                                if connected.user1 == user and connected.user2 in actual_users:
                                    notify_users.append(connected.user2)
                                elif connected.user2 == user and connected.user1 in actual_users:
                                    notify_users.append(connected.user1)
                        else:
                            notify_users = actual_users
                        for notify in notify_users:
                            Notify.objects.create(user1=notify,user2=user)

            return HttpResponseRedirect(reverse('viewtweet', args=(user,)))
        return render(request, 'twitter/add_tweet.html', {
            'form': tweetForm,
        })


class Logout(generic.View):
    http_method_names = ['dispatch', 'get']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Logout, self).dispatch( *args, **kwargs)

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('login'))


class Signup(generic.View):
    http_method_names = ['get','post']

    def get(self, request, *args, **kwargs):
        form = SignupForm()
        return render(request, 'twitter/signup_form.html', {
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('login'))
        return render(request, 'twitter/signup_form.html', {
            'form': form,
        })