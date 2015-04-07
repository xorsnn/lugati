from django.conf.urls import patterns, include, url
#from partners.sales_points.views import ListSalesPoints, CreateSalesPoint, UpdateSalesPoint, DeleteSalesPoint
from lugati.lugati_points_of_sale.models import SalesPoint
from lugati.lugati_points_of_sale.views import ListSalesPoints, CreateSalesPoint, UpdateSalesPoint, DeleteSalesPoint
#from lugati.lugati_points_of_sale.views import ListCities, CreateCity, UpdateCity, DeleteCity

urlpatterns = patterns('',

    url(r'^$', ListSalesPoints.as_view(), name='list_sales_points'),
    url(r'^get_points_of_sale/$', 'lugati.lugati_points_of_sale.views.get_points_of_sale', name='get_points_of_sale'),

    url(r'^create/$', CreateSalesPoint.as_view(), name='create_sales_point'),
    url(r'^update/(?P<pk>\w+)/$', UpdateSalesPoint.as_view(), name='update_sales_point'),
    url(r'^delete/(?P<pk>\w+)/$', DeleteSalesPoint.as_view(), name='delete_sales_point'),


    url(r'^cities/get_regions/$', 'lugati.lugati_points_of_sale.views.get_regions', name='get_regions'),
    url(r'^cities/get_delivery_regions/$', 'lugati.lugati_points_of_sale.views.get_delivery_regions', name='get_delivery_regions'),


    url(r'^cities/get_countries_list/$', 'lugati.lugati_points_of_sale.views.get_countries_list', name='get_countries_list'),
    url(r'^cities/get_cities_list/$', 'lugati.lugati_points_of_sale.views.get_cities_list', name='get_cities_list'),

    url(r'^get_nearest/$', 'lugati.lugati_points_of_sale.views.get_nearest_sales_points', name='get_nearest_sales_points'),
    url(r'^get_nearest_city/$', 'lugati.lugati_points_of_sale.views.get_nearest_city', name='get_nearest_sales_city'),
    url(r'^get_city_points_of_sale/$', 'lugati.lugati_points_of_sale.views.get_city_points_of_sale', name='get_city_points_of_sale'),
    url(r'^get_nearest_points_of_sale/$', 'lugati.lugati_points_of_sale.views.get_nearest_points_of_sale', name='get_nearest_points_of_sale'),
    url(r'^get_additional_points_of_sale/$', 'lugati.lugati_points_of_sale.views.get_additional_points_of_sale', name='get_additional_points_of_sale'),


)