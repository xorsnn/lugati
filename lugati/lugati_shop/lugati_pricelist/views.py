from django.shortcuts import render
from lugati.lugati_shop.lugati_pricelist.models import PriceList, PriceListItem
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import resolve
from django.http import HttpResponse
import json

def manage_pricelists_ajax_new(request):
    cur_site = get_current_site(request)
    #cat_id = request.GET['cat_id']
    #res_dt = []
    def get_pricelists_tree(parent_object=None, level=0):
        dt = []
        pricelists = PriceList.objects.all()
        for pricelist in pricelists:
            cur_node = {
                'label': pricelist.name,
                'uid': pricelist.id,
                'data': {
                    'definition': pricelist.name
                }
            }

            dt.append(cur_node)
        return dt

    res_dt = get_pricelists_tree()
    return HttpResponse(json.dumps(res_dt))

class ListPriceLists(ListView):
    model = PriceList
    template_name = 'lugati_shop/lugati_pricelist/list_pricelists.html'


class CreatePricelist(CreateView):
    model = PriceList
    template_name = 'lugati_shop/lugati_pricelist/create_pricelist.html'
    success_url = '/lugati_admin/lugati_shop/pricelists/'

    def get_initial(self):
        res = {}
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

class UpdatePriceList(UpdateView):
    model = PriceList
    template_name = 'lugati_shop/lugati_pricelist/update_pricelist.html'
    success_url = '/lugati_admin/lugati_shop/pricelists/'

    def get_initial(self):
        res = {}
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

#class CreatePricelistItem(CreateView):
#    model = PriceListItem
#    template_name = 'lugati_admin/lugati_shop/lugati_pricelist/create_pricelist_item.html'
#    success_url = '/lugati_admin/lugati_shop/pricelists/'
#
#    def get_initial(self):
#        res = {}
#        cur_site = get_current_site(self.request)
#        res['site'] = cur_site
#        return res
#
#    def form_invalid(self, form):
#        if self.request.is_ajax():
#            form_errors = {}
#            for k in form.errors:
#                form_errors[k] = form.errors[k][0]
#            res_dt = {
#                'error': True,
#                'form_errors': form_errors
#            }
#            return HttpResponse(json.dumps(res_dt))
#    def form_valid(self, form):
#        self.object = form.save()
#        if self.request.is_ajax():
#            res_dt = {
#                'error': False
#            }
#            return HttpResponse(json.dumps(res_dt))
#
