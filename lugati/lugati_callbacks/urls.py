from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^test_callback/$', 'lugati.lugati_callbacks.views.test_callback', name='test_callback'),
)
