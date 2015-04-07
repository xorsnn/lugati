from django.shortcuts import render
from .models import DeliveryOption
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.http import HttpResponse
import json
from django.contrib.sites.models import get_current_site
from .forms import DeliveryOptionForm

def get_delivery_control_panel(request):
    return render(request, 'lugati_admin/lugati_shop/lugati_delivery/delivery_control_panel.html')
def get_delivery_options_tree(request):
    cur_site = get_current_site(request)

    def get_delivery_options_tree(order_group=None, level=0):
        dt = []
        orders = DeliveryOption.objects.filter(site=cur_site).order_by('id')
        for order in orders:
            cur_node = {
                'label': order.name,
                'uid': order.id,
                'data': {
                    'definition': order.id
                }
            }
            dt.append(cur_node)
        return dt

    res_dt = get_delivery_options_tree()
    return HttpResponse(json.dumps(res_dt))


class CreateDeliveryOption(CreateView):
    model = DeliveryOption
    template_name = 'lugati_admin/lugati_shop/lugati_delivery/create_delivery_option.html'
    success_url = '/lugati_admin/'
    form_class = DeliveryOptionForm

    def get_initial(self):
        cur_site = get_current_site(self.request)
        res = {
            'site': cur_site
        }
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


class UpdateDeliveryOption(UpdateView):
    model = DeliveryOption
    template_name = 'lugati_admin/lugati_shop/lugati_delivery/edit_delivery_option.html'
    success_url = '/lugati_admin/'
    form_class = DeliveryOptionForm

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
