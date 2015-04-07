from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^get_weekly_report/$', 'lugati.lugati_shop.lugati_reports.views.get_weekly_report', name='get_weekly_report'),
)
