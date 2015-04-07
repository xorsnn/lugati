from django.conf.urls import patterns, include, url
#from .views import ListOrder, CreateOrder, UpdateOrder, DeleteOrder, DetailOrder
from .views_admin import UpdateOrder
urlpatterns = patterns('',
    url(r'^get_orders_tree/$', 'lugati.lugati_shop.lugati_orders.views_admin.get_orders_tree', name='get_orders_tree'),
    url(r'^get_orders_control_panel/$', 'lugati.lugati_shop.lugati_orders.views_admin.get_orders_control_panel', name='get_orders_control_panel'),

    #url(r'^clerks/create/$', CreateClerk.as_view(), name='create_clerk'),
    url(r'^update/(?P<pk>\w+)/$', UpdateOrder.as_view(), name='update_order'),
)