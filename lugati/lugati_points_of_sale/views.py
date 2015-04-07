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
from .forms import PosForm
from lugati.lugati_shop.lugati_delivery.models import DeliveryOption
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

def reverse_numeric(x, y):
    if (float(y['dist']) < float(x['dist'])):
        return 1
    else:
        return -1
    #return (float(x['dist'])-float(y['dist']))

#sales points
def get_points_of_sale(request):
    cur_site = get_current_site(request)
    def get_points_of_sale_tree(parent_object=None, level=0):
        dt = []
        points_of_sale = SalesPoint.objects.all()
        for point_of_sale in points_of_sale:
            cur_node = {
                'label': point_of_sale.name,
                'uid': point_of_sale.id,
                'data': {
                    'definition': point_of_sale.name
                }
            }

            dt.append(cur_node)
        return dt

    res_dt = get_points_of_sale_tree()
    return HttpResponse(json.dumps(res_dt))

class ListSalesPoints(ListView):
    model = SalesPoint
    template_name = 'lugati_admin/points_of_sale/sales_points_list_new.html'


class CreateSalesPoint(CreateView):
    model = SalesPoint
    form_class = PosForm
    template_name = 'lugati_admin/points_of_sale/create_sales_point_new.html'
    success_url = '/lugati_admin/points_of_sale/'

    def get_initial(self):
        res = {}
        cur_site = get_current_site(self.request)
        res['site'] = cur_site
        return res

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
class UpdateSalesPoint(UpdateView):
    model = SalesPoint
    form_class = PosForm
    #template_name = 'lugati_admin/points_of_sale/create_sales_point.html'
    template_name = 'lugati_admin/points_of_sale/update_sales_point_new.html'
    success_url = '/lugati_admin/points_of_sale/'

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

class DeleteSalesPoint(DeleteView):
    model = SalesPoint
#~


def get_nearest_sales_points(request):
    lng = float(request.POST['lng'])
    lat = float(request.POST['lat'])
    points_of_sale = SalesPoint.objects.all()
    points = []
    for point in points_of_sale:
        p_lat = float(point.lat)
        p_lng = float(point.lng)

        dist = math.sqrt((p_lat-lat)**2+(p_lng-lng)**2)
        points.append({
            'point_id': point.id,
            'dist': dist,
            'point_name': point.name,
            'link': point.link,
            'address': point.address.strip()
        })
    res = {}
    index = 0
    for point in sorted(points, cmp=reverse_numeric)[0:5]:
        res['point_'+str(index)] = point
        index += 1
    return HttpResponse(json.dumps({'points':res}))

@csrf_exempt
def get_nearest_city(request):
    logger.info('access_nearest ->')
    cur_site = get_current_site(request)
    #lng = float(request.POST['lng'])
    #lat = float(request.POST['lat'])
    lng = float(request.GET['lng'])
    lat = float(request.GET['lat'])
    cities = City.objects.filter(site=cur_site).filter(is_region=False)
    points = []
    for city in cities:
        p_lat = float(city.lat)
        p_lng = float(city.lng)

        dist = math.sqrt((p_lat-lat)**2+(p_lng-lng)**2)
        points.append({
            'city_id': city.id,
            'region_id': city.region.id,
            'dist': dist,
            'point_name': city.name
        })

    points = sorted(points, cmp=reverse_numeric)
    point = points[0]

    return HttpResponse(json.dumps(point))

@csrf_exempt
def get_additional_points_of_sale(request):
    cur_site = get_current_site(request)


    from lugati.lugati_procs import get_ids
    from lugati.products.models import Product

    try:
        cat_id, prod_id = get_ids(request, request.GET['cur_path'])
    except:
        cat_id = None
        prod_id= None

    points = []
    additional_points = SalesPoint.objects.filter(site=cur_site).filter(city=None).filter(product=Product.objects.get(pk=prod_id))
    for point in additional_points:
        points.append({
            'point_id': point.id,
            'point_name': point.name,
            'link': point.link,
            'address': point.address.strip()
        })
    index = 0
    res = {}
    for point in points:
        res['point_'+str(index)] = point
        index += 1

    return HttpResponse(json.dumps({'points':res}))

@csrf_exempt
def get_city_points_of_sale(request):
    cur_site = get_current_site(request)
    #city_id = float(request.POST['city_id'])
    city_id = float(request.GET['city_id'])

    from lugati.lugati_procs import get_ids
    from lugati.products.models import Product

    try:
        cat_id, prod_id = get_ids(request, request.GET['cur_path'])
    except:
        cat_id = None
        prod_id= None

    if prod_id:
        sales_points = SalesPoint.objects.filter(site=cur_site).filter(city=City.objects.get(pk=city_id)).filter(product=Product.objects.get(pk=prod_id))
    else:
        sales_points = []

    points = []
    for point in sales_points:
        points.append({
            'point_id': point.id,
            'point_name': point.name,
            'link': point.link,
            'address': point.address.strip()
        })

    index = 0
    res = {}
    for point in points:
        res['point_'+str(index)] = point
        index += 1

    return HttpResponse(json.dumps({'points':res}))

@csrf_exempt
def get_nearest_points_of_sale(request):

    cur_site = get_current_site(request)
    from lugati.lugati_procs import get_ids
    from lugati.products.models import Product


    lng = float(request.GET['lng'])
    lat = float(request.GET['lat'])
    try:
        cat_id, prod_id = get_ids(request, request.GET['cur_path'])
    except:
        cat_id = None
        prod_id= None

    if prod_id:
        sales_points = SalesPoint.objects.filter(site=cur_site).filter(product=Product.objects.get(pk=prod_id))
    else:
        sales_points = []
    points = []
    for point in sales_points:
        if (str(point.lat).strip() <> '') and (str(point.lng).strip() <> ''):
            try:
                p_lat = float(point.lat)
                p_lng = float(point.lng)

                dist = math.sqrt((p_lat-lat)**2+(p_lng-lng)**2)

                points.append({
                    'dist': dist,
                    'point_id': point.id,
                    'point_name': point.name,
                    'link': point.link,
                    'address': point.address.strip()
                })
            except:
                pass

    index = 0
    res = {}
    for point in sorted(points, cmp=reverse_numeric):
        res['point_'+str(index)] = point
        index += 1

    return HttpResponse(json.dumps({'points':res}))

def get_countries_list(request):
    cur_site = get_current_site(request)
    cities = City.objects.filter(site=cur_site).filter(is_region=True).order_by('name')
    res_dt = []
    for city in cities:
        res_dt.append({
            'id': city.id,
            'name': city.name
        })
    return HttpResponse(json.dumps(res_dt))

def get_cities_list(request):
    cur_site = get_current_site(request)
    cities = City.objects.filter(site=cur_site).filter(is_region=False).order_by('name')
    res_dt = []
    for city in cities:
        if city.region:
            res_dt.append({
                'id': city.id,
                'region': city.region.id,
                'name': city.name
            })
    return HttpResponse(json.dumps(res_dt))

def get_regions(request):
    cur_site = get_current_site(request)
    def get_tree(region=None):
        res = []
        cities = City.objects.filter(site=cur_site).filter(region=region).order_by('-priority', 'name')
        for city in cities:
            node = {
                'name': city.name,
                'id': city.id,
                'children': get_tree(city)
            }
            res.append(node)
        return res

    return HttpResponse(json.dumps(get_tree()))

def get_delivery_regions(request):
    cur_site = get_current_site(request)
    def get_tree(region=None):
        res = []

        cities = City.objects.filter(Q(pk__in=set(DeliveryOption.objects.filter(site=cur_site).filter(active=True).values_list('city', flat=True).distinct())) | Q(pk__in=set(City.objects.filter(site=cur_site).values_list('region', flat=True).distinct()))).filter(region=region).order_by('-priority', 'name')
        for city in cities:
            node = {
                'name': city.name,
                'id': city.id,
                'children': get_tree(city)
            }
            res.append(node)
        return res

    return HttpResponse(json.dumps(get_tree()))