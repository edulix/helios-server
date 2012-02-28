# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns(
    '',
    (r'^auth/', include('auth.urls')),
    (r'^helios/', include('helios.urls')),

    # SHOULD BE REPLACED BY APACHE STATIC PATH
    (r'booth/(?P<path>.*)$', 'views.serve_templates', {'document_root' : settings.ROOT_PATH + '/heliosbooth'}),
    (r'verifier/(?P<path>.*)$', 'views.serve_templates', {'document_root' : settings.ROOT_PATH + '/heliosverifier'}),

    (r'static/auth/(?P<path>.*)$', 'views.serve_templates', {'document_root' : settings.ROOT_PATH + '/auth/media'}),
    (r'static/helios/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.ROOT_PATH + '/helios/media'}),
    (r'static/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : settings.ROOT_PATH + '/server_ui/media'}),

    (r'^', include('server_ui.urls')),

    )

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )
