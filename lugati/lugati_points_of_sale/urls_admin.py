from django.conf.urls import patterns, include, url
#from partners.sales_points.views import ListSalesPoints, CreateSalesPoint, UpdateSalesPoint, DeleteSalesPoint
from lugati.lugati_points_of_sale.models import SalesPoint
from lugati.lugati_points_of_sale.views import ListSalesPoints, CreateSalesPoint, UpdateSalesPoint, DeleteSalesPoint
from lugati.lugati_points_of_sale.views_admin import CreateCity, UpdateCity, DeleteCity

urlpatterns = patterns('',
    url(r'^get_points_of_sale_tree/$', 'lugati.lugati_points_of_sale.views_admin.get_points_of_sale_tree', name='get_points_of_sale_tree'),
    url(r'^get_form/(?P<pk>\w+)/$', UpdateSalesPoint.as_view(), name='get_form'),
    url(r'^get_points_of_sale_control_panel/$', 'lugati.lugati_points_of_sale.views_admin.get_points_of_sale_control_panel', name='get_points_of_sale_control_panel'),

    url(r'^cities/$', 'lugati.lugati_points_of_sale.views_admin.list_cities', name='list_cities'),
    url(r'^cities/create_region/$', CreateCity.as_view(), name='create_region'),
    url(r'^cities/create/$', CreateCity.as_view(), name='create_city'),
    url(r'^cities/get_form/(?P<pk>\w+)/$', UpdateCity.as_view(), name='update_city'),

    url(r'^cities/delete/(?P<pk>\w+)/$', DeleteCity.as_view(), name='delete_city'),
    url(r'^cities/get_cities_tree/$', 'lugati.lugati_points_of_sale.views_admin.get_cities_tree_ajax', name='get_cities_tree_ajax'),
)