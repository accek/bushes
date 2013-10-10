from django.conf import settings
from django.conf.urls import patterns, include, url
import bushes.registration_backend

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'bushes.views.index_view', name='index'),

    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

for app in settings.INSTALLED_APPS:
    if app.startswith('oioioi.'):
        try:
            urls_module = import_module(app + '.urls')
            urlpatterns += getattr(urls_module, 'urlpatterns')
        except ImportError:
            pass

urlpatterns += bushes.registration_backend.urlpatterns
