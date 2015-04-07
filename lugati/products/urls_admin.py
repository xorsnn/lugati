from django.conf.urls import patterns, include, url
from .views_admin import CreateProduct, UpdateProduct, DeleteProduct
from .views_admin import CreateBrand, UpdateBrand

urlpatterns = patterns('',
    url(r'^get_promo_tree/$', 'lugati.products.views_admin.get_promo_tree', name='get_promo_tree'),
    url(r'^get_products_control_panel/$', 'lugati.products.views_admin.get_products_control_panel', name='get_products_control_panel'),

    url(r'^create/(?P<node_type>\w+)/$', CreateProduct.as_view(), name='create product'),
    url(r'^update/(?P<pk>\w+)/$', UpdateProduct.as_view(), name='update_product'),
    url(r'^delete/(?P<pk>\w+)/$', DeleteProduct.as_view(), name='delete product'),

    #brands
    url(r'^get_brands_tree/$', 'lugati.products.views_admin.get_brands_tree', name='get_brands_tree'),
    url(r'^brands/create/$', CreateBrand.as_view(), name='create brand'),
    url(r'^brands/update/(?P<pk>\w+)/$', UpdateBrand.as_view(), name='update_brand'),
    #url(r'^delete/(?P<node_type>\w+)/(?P<pk>\w+)/$', DeleteProduct.as_view(), name='delete product'),

    url(r'^get_brands_control_panel/$', 'lugati.products.views_admin.get_brands_control_panel', name='get_brands_control_panel'),
)
