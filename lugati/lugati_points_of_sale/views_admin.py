from django.shortcuts import render
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, DetailView
from lugati.lugati_points_of_sale.models import SalesPoint, City
from lugati.lugati_points_of_sale.forms import CityForm
from django.contrib.sites.models import get_current_site
import math
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import resolve

import logging
logger = logging.getLogger(__name__)

def get_points_of_sale_control_panel(request):
    return render(request, 'lugati_admin/points_of_sale/points_of_sale_control_panel.html')

def get_points_of_sale_tree(request):
    dt = []
    sales_points = SalesPoint.objects.all()
    for sales_point in sales_points:

        cur_node = {
            'label': sales_point.name,
            'uid': sales_point.id,
            'data': {
                'definition': sales_point.name
            }
        }

        dt.append(cur_node)

    return HttpResponse(json.dumps(dt))

class UpdateSalesPoint(UpdateView):
    model = SalesPoint
    #template_name = 'lugati_admin/points_of_sale/create_sales_point.html'
    template_name = 'lugati_admin/points_of_sale/update_sales_point_new.html'
    success_url = '/lugati_admin/points_of_sale/'

#cities
def get_cities_tree_ajax(request):
    cur_site = get_current_site(request)

    def get_cities_tree(region=None, level=0):
        dt = []
        cities = City.objects.filter(site=cur_site).filter(region=region).order_by('is_region', 'name')
        for city in cities:
            cur_node = {
                'label': city.name,
                'uid': city.id,
                'data': {
                    'definition': city.name
                }
            }
            children = City.objects.filter(region = city)
            if children.exists():
                cur_node['children'] = get_cities_tree(region=city, level=level+1)
            dt.append(cur_node)
        return dt

    res_dt = get_cities_tree()
    return HttpResponse(json.dumps(res_dt))

def list_cities(request):
    return render(request, 'lugati_admin/cities/list_cities_new.html')

class CreateCity(CreateView):
    model = City
    template_name = 'lugati_admin/cities/create_city.html'
    success_url = '/lugati_admin/points_of_sale/cities/'

    form_class = CityForm

    def get_initial(self):
        res = {}

        match = resolve(self.request.path)
        if match.url_name == 'create_region':
            res['is_region'] = True
        else:
            res['is_region'] = False
        cur_site = get_current_site(self.request)
        res['site'] = cur_site
        return res
    def form_invalid(self, form):
        if self.request.is_ajax():
            form_errors = {}
            for k in form.errors:
                form_errors[k] = form.errors[k][0]
            res_dt = {
                'error': True,
                'form_errors': form_errors
            }
            return HttpResponse(json.dumps(res_dt))
    def form_valid(self, form):
        self.object = form.save()

        if self.request.is_ajax():
            res_dt = {
                'error': False
            }
            return HttpResponse(json.dumps(res_dt))

class UpdateCity(UpdateView):
    model = City
    template_name = 'lugati_admin/cities/update_city.html'
    success_url = '/lugati_admin/points_of_sale/cities/'

    def form_invalid(self, form):
        if self.request.is_ajax():
            res_dt = {
                'error': True
            }
            return HttpResponse(json.dumps(res_dt))
    def form_valid(self, form):
        self.object = form.save()

        if self.request.is_ajax():
            res_dt = {
                'error': False
            }
            return HttpResponse(json.dumps(res_dt))

class DeleteCity(DeleteView):
    model = City
#~