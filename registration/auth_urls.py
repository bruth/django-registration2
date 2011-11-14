from django.conf.urls.defaults import *

urlpatterns = patterns('django.contrib.auth.views', 
    url(r'^login/$', 'login', {
        'template_name': 'registration/login.html'
    }, name='login'),
    
    url(r'^logout/$', 'logout_then_login', {
        'template_name': 'registration/logout.html'
    }, name='logout'),

    url(r'^password/change/$', 'logout_then_login',
        name='auth_password_change'),

    url(r'^password/change/done/$', 'password_change_done',
        name='auth_password_change_done'),

    url(r'^password/reset/$', 'password_reset',
        name='auth_password_reset'),

    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'password_reset_confirm',
        name='auth_password_reset_confirm'),

    url(r'^password/reset/complete/$', 'password_reset_complete',
        name='auth_password_reset_complete'),
       
    url(r'^password/reset/done/$', 'password_reset_done',
        name='auth_password_reset_done'),
)