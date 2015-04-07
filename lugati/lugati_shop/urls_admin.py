from django.conf.urls import patterns, include, url
#from .views import CreateProduct, UpdateProduct, DeleteProduct
# from .views_admin import UpdateShoppingPlace, DeleteShoppingPlace, CreateShoppingPlace
from .views_admin import CreatePhoneNumber, UpdatePhoneNumber

urlpatterns = patterns('',

    url(r'^lugati_reports_admin/', include('lugati.lugati_shop.lugati_reports.urls', namespace='lugati_reports_admin')),

    url(r'^lugati_orders_admin/', include('lugati.lugati_shop.lugati_orders.urls_admin', namespace='lugati_orders_admin')),
    url(r'^lugati_delivery_admin/', include('lugati.lugati_shop.lugati_delivery.urls_admin', namespace='lugati_delivery_admin')),

    url(r'^get_shops_tree/$', 'lugati.lugati_shop.views_admin.get_shops_tree', name='get_shops_tree'),
    # url(r'^get_form/(?P<pk>\w+)/$', UpdateShopSetting.as_view(), name='get_form'),

    url(r'^get_shopping_places_tree/$', 'lugati.lugati_shop.views_admin.get_shopping_places_tree', name='get_shopping_places_tree'),
    url(r'^get_shopping_places_control_panel/$', 'lugati.lugati_shop.views_admin.get_shopping_places_control_panel', name='get_shopping_places_control_panel'),

    # url(r'^shopping_places/create/$', CreateShoppingPlace.as_view(), name='create_shopping_place'),
    # url(r'^shopping_places/update/(?P<pk>\w+)/$', UpdateShoppingPlace.as_view(), name='update_shopping_place'),
    # url(r'^shopping_places/delete/(?P<pk>\w+)/$', DeleteShoppingPlace.as_view(), name='delete_shopping_place'),
#clerks
    url(r'^get_clerks_tree/$', 'lugati.lugati_shop.views_admin.get_clerks_tree', name='get_clerks_tree'),
    url(r'^get_clerks_control_panel/$', 'lugati.lugati_shop.views_admin.get_clerks_control_panel', name='get_clerks_control_panel'),

    # url(r'^clerks/create/$', CreateClerk.as_view(), name='create_clerk'),
    # url(r'^clerks/update/(?P<pk>\w+)/$', UpdateClerk.as_view(), name='update_clerk'),
#phones
    url(r'^get_phones_tree/$', 'lugati.lugati_shop.views_admin.get_phones_tree', name='get_phones_tree'),
    url(r'^get_phones_control_panel/$', 'lugati.lugati_shop.views_admin.get_phones_control_panel', name='get_phones_control_panel'),

    url(r'^phones/create/$', CreatePhoneNumber.as_view(), name='create_phone'),
    url(r'^phones/update/(?P<pk>\w+)/$', UpdatePhoneNumber.as_view(), name='update_phone'),
)
