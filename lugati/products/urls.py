from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^manage/$', 'lugati.products.views.manage_products', name='manage products'),

    url(r'^delete_thumbnail/(?P<product_id>\w+)/$', 'lugati.products.views.delete_thumbnail', name='delete thumbnail'),

    url(r'^product/(?P<pr_id>\w+)/$', 'lugati.products.views.product_page', name='product_page'),

    #api
    url(r'^get_products/$', 'lugati.products.views.get_products', name='get_products'),
)
