from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from twitter.models import *


class NotifyAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'read')
    actions = ['make_read', 'make_unread']
    raw_id_fields = ('user1', 'user2')

    def make_read(self, request, queryset):
        rows_updated = queryset.update(read=True)
        if rows_updated == 1:
            message_bit = '1 notification was'
        else:
            message_bit = '%s notifications were' % rows_updated
        self.message_user(request, '%s successfully marked as read.' % message_bit)
    make_read.short_description = 'Mark as read'

    def make_unread(self, request, queryset):
        rows_updated = queryset.update(read=False)
        if rows_updated == 1:
            message_bit = '1 notification was'
        else:
            message_bit = '%s notifications were' % rows_updated
        self.message_user(request, '%s successfully marked as unread.' % message_bit)
    make_unread.short_description = 'Mark as unread'


class TweetAdmin(admin.ModelAdmin):
    list_display = ('message', 'group', 'make_public')
    raw_id_fields = ('user',)

    def make_public(self, obj):
        if obj.group == Tweet.public:
            return ''
        str_url = reverse('admin:make_public', args=(obj.id,))
        return '<a href="%s">Make Public</a>' % str_url
    make_public.allow_tags = True

    def get_urls(self):
        urls = super(TweetAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^makepublic/(?P<tweet_id>\d+)/$', self.admin_site.admin_view(self.update_tweet), name='make_public')
        )
        return my_urls + urls

    def update_tweet(self, request, tweet_id):
        Tweet.objects.filter(id__exact=tweet_id).update(group=Tweet.public)
        messages.success(request, 'Tweet updated successfully.')
        return HttpResponseRedirect(reverse('admin:twitter_tweet_changelist'))


class ConnectAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'is_active')
    raw_id_fields = ('user1', 'user2')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'dob', 'interests')
    raw_id_fields = ("user",)


# admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Site)
admin.site.register(Notify, NotifyAdmin)
admin.site.register(Tweet, TweetAdmin)
admin.site.register(Profile,ProfileAdmin)
admin.site.register(Connect, ConnectAdmin)
admin.site.register(Reject)
