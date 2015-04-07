from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'lugati.lugati_feedback.views.lugati_feedback', name='lugati_feedback'),
    url(r'^lugati_newsletter_sing_up/$', 'lugati.lugati_feedback.views.lugati_newsletter_sing_up', name='lugati_newsletter_sing_up'),
    url(r'^mps_feedback/$', 'lugati.lugati_feedback.views.mps_feedback', name='mps_feedback'),
)
