from django.conf.urls import patterns, include, url
from lugati.lugati_registration.views import LugatiRegistrationView

urlpatterns = patterns('',
#registration
    url(r'^accounts/register/$', LugatiRegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.urls')),
#~registration
)
