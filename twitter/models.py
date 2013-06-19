from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User)
    dob = models.DateField(blank=True, null=True)
    interests = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return 'Profile of ' + self.user.username


class Tweet(models.Model):
    public = 'public'
    private = 'private'
    friends = 'friends'
    GROUP_CHOICES = (
        (public, 'Public'),
        (private, 'Private'),
        (friends, 'Friends'),
    )
    user = models.ForeignKey(User)
    message = models.TextField()
    group = models.CharField(max_length=7, choices=GROUP_CHOICES, default=public)
    added_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.message


class Connect(models.Model):
    user1 = models.ForeignKey(User)
    user2 = models.ForeignKey(User, related_name='to')
    is_active = models.BooleanField(default=False)
    confirmation_code = models.CharField(max_length=50)

    def __unicode__(self):
        return 'Connection between ' + self.user1.username + ' and ' + self.user2.username

    class Meta:
        verbose_name_plural = 'connections'


class Notify(models.Model):
    user1 = models.ForeignKey(User)
    user2 = models.ForeignKey(User, related_name='from')
    read = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user2.username + ' added a tweet related to ' + self.user1.username

    class Meta:
        verbose_name_plural = 'notifications'


class Reject(models.Model):
    user1 = models.ForeignKey(User)
    user2 = models.ForeignKey(User, related_name='reject_to')

    def __unicode__(self):
        return self.user1.username + ' rejects connect request from ' + self.user2.username

    class Meta:
        verbose_name_plural = 'rejections'