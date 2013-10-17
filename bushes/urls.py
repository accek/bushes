from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
import bushes.registration_backend

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'bushes.views.index_view', name='index'),
    url(r'^a/(?P<id>\d+)$', 'bushes.views.assignment_view', name='assignment'),
    url(r'^s/(?P<id>\d+)$', 'bushes.views.sentence_view', name='sentence'),
    url(r'^clone/(?P<tree_id>\d+)$', 'bushes.views.clone_view', name='clone_tree'),
    url(r'^manifest.appcache$',
        'bushes.views.manifest_view', name='index_manifest'),
    url(r'^upload$', 'bushes.views.upload_view', name='upload'),
    url(r'^more$', 'bushes.views.more_view', name='more'),
    url(r'^return$', 'bushes.views.return_view', name='return'),

    url(r'^badbrowser/$',
        TemplateView.as_view(template_name='badbrowser.html'),
        name='badbrowser'),

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
