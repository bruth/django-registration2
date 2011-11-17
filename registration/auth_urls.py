from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('django.contrib.auth.views', 
    url(r'^login/$', 'login', {
        'template_name': 'registration/login.html'
    }, name='login'),
    
    url(r'^logout/$', 'logout_then_login', {
        'template_name': 'registration/logout.html'
    }, name='logout'),

    url(r'^password/reset/$', 'password_reset',
        name='password-reset'),

    url(r'^password/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'password_reset_confirm', name='password-reset-confirm'),

    url(r'^password/reset/complete/$', 'password_reset_complete',
        name='password-reset-complete'),
)
