from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'lugati.lugati_static.views.static_page', name='static_page'),
    #url(r'^(?P<page_name>[\w\S]+)/$', 'lugati.lugati_static.views.static_page', name='static_page'),
    url(r'^(?P<page_name>\w+)/$', 'lugati.lugati_static.views.static_page', name='static_page'),
    #url(r'^$', include('lugati.lugati_static.urls', namespace='lugati_static')),
    #url(r'^products/', include('lugati.products.urls', namespace='products')),
    #url(r'^lugati_admin/', include('lugati.lugati_admin.urls')),
)
