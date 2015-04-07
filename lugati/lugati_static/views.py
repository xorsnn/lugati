from django.shortcuts import render, redirect
from django.contrib.sites.models import get_current_site
from django.conf import settings
from django.core.urlresolvers import resolve
from django.views.generic.edit import UpdateView
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.forms import FlatpageForm
from django.http import JsonResponse
import json

class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response

class LugatiFlatPageUpdateView(AjaxableResponseMixin, UpdateView):
    model = FlatPage
    form_class = FlatpageForm

    def get_form_kwargs(self):
        response = super(LugatiFlatPageUpdateView, self).get_form_kwargs()
        site = get_current_site(self.request)
        bodyDt = json.loads(self.request.body)
        bodyDt['url'] = '/' + self.kwargs['url'] + '/'
        bodyDt['title'] = self.kwargs['url'].replace('/', '_')
        bodyDt['sites'] = [site.id]
        response['data'] = bodyDt

        # response['data'].update(json.loads(self.request.body))
        return response

    def get_object(self):
        return FlatPage.objects.get(sites__in=[get_current_site(self.request)], url=('/' + self.kwargs['url'] + '/'))

def static_page(request, page_name = ''):
    current_site = get_current_site(request)
    cur_site_name = current_site.name
    LugatiFlatPageUpdateView.as_view()
    resp_data = {
        'lugati_debug': settings.DEBUG,
        'cur_site_name': cur_site_name,
        'request': request
    }

    if settings.SHOP_TYPE == 'MPS':
        if page_name == 'ng_catalog_template':
            if 'cur_path' in request.GET:
                resolved_path = resolve(request.GET['cur_path'])
                try:
                    pos_id = resolved_path.kwargs['pos_id']
                    resp_data['pos_id'] = pos_id
                except:
                    pass

    template_name = 'main.html'
    if page_name <> '':
        template_name = page_name + '.html'
    if (settings.SHOP_TYPE == 'MPS') and (page_name == ''):
        return redirect('/lugati_admin/lugati_login/')
    else:
        return render(request, 'custom/' + current_site.name + '/' + template_name, resp_data)