# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
#from .forms import AddCategoryForm, AddProductForm
from .models import Product, ProductPrice, Bestseller, Brand
from .forms import ProductForm, NgProductForm, CategoryForm

from django.conf import settings
from django.contrib.sites.models import get_current_site
import json
from lugati.lugati_media.models import ThebloqImage

from django.contrib.auth import logout
from django.core import serializers
from django.forms.models import model_to_dict
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from lugati.lugati_shop.lugati_promo.models import SpecialOffer
from django.template.loader import get_template
from django.template import Context
from lugati.lugati_registration.models import LugatiUserProfile
import logging
logger = logging.getLogger(__name__)

def get_products_control_panel(request):
    res_dt = {'lugati_filter': False}
    cur_site = get_current_site(request)
    if cur_site.name == 'primorsk':
        res_dt['lugati_filter'] = True
    return render(request, 'lugati_admin/products/products_control_panel.html', res_dt)

def get_promo_tree(request):
    cur_site = get_current_site(request)
    cur_profile = LugatiUserProfile.objects.get(user=request.user)
    def get_products_tree(parent_object=None, level=0):
        dt = []
        #ids = []
        #for id_new in SpecialOffer.objects.all()
        #    ids.append(SpecialOffer.)
        products = Product.objects.filter(site=cur_site).filter(is_category=False).filter(pk__in=SpecialOffer.objects.all()).order_by('is_category', 'priority')
        if settings.LUGATI_SPLIT_CATALOG_BY_SHOP:
            products = products.filter(shop=cur_profile.main_shop)
        for product in products:
            cur_node = {
                'label': product.name,
                'uid': product.id,
                'data': {
                    'definition': product.preview
                }
            }

            dt.append(cur_node)
        return dt
    res_dt = get_products_tree()
    return HttpResponse(json.dumps(res_dt))


class CreateProduct(CreateView):
    model = Product
    template_name = 'products/create_product_new.html'
    success_url = '/lugati_admin/#/products'

    def get_form_class(self):
        if self.kwargs['node_type'] == 'product':
            return ProductForm
        else:
            return CategoryForm

    def get_initial(self):
        res = {}
        if self.kwargs['node_type'] == 'category':
            res['is_category'] = True
        cur_site = get_current_site(self.request)
        res['site'] = cur_site
        if settings.LUGATI_SPLIT_CATALOG_BY_SHOP:
            cur_profile = LugatiUserProfile.objects.get(user=self.request.user)
            res['shop'] = cur_profile.main_shop
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
        pic_id_str = form.cleaned_data['pic_array']
        pic_id_array = pic_id_str.split(';')
        for pic_id in pic_id_array:
            if pic_id <> '':
                try:
                    tb_image = ThebloqImage.objects.get(id=pic_id)
                    tb_image.content_object = self.object
                    tb_image.save()
                except:
                    logger.info('image with id ' + str(pic_id) + " doesn't exists")
                #self.object.assignImage(ThebloqImage.objects.get(id=pic_id).file)
        if not self.object.is_category:
            self.object.setPrice(form.cleaned_data['price'])
            if form.cleaned_data['is_promo']:
                try:
                    sp_offer = SpecialOffer.objects.get(pk=self.object)
                except:
                    sp_offer = SpecialOffer()
                    sp_offer.product = self.object
                    sp_offer.save()

            #properties.set_promo(form.cleaned_data['is_promo'], self.object)
            #properties.set_as_product_of_the_month(form.cleaned_data['is_product_of_the_month'], self.object)
            if form.cleaned_data['bestseller']:
                if not Bestseller.objects.filter(product=self.object).exists():
                    bestseller = Bestseller()
                    bestseller.product = self.object
                    bestseller.save()
            else:
                Bestseller.objects.filter(product=self.object).delete()

        if self.request.is_ajax():
            res_dt = {
                'error': False
            }
            return HttpResponse(json.dumps(res_dt))
        else:
            return super(CreateProduct, self).form_valid(form)


class UpdateProduct(UpdateView):
    model = Product
    template_name = 'products/edit_product_new.html'
    success_url = '/lugati_admin/#/products'

    def get_form_class(self):
        #if self.kwargs['node_type'] == 'product':
        #    return ProductForm
        #else:
        #    return CategoryForm

        if self.object.is_category:
            return CategoryForm
        else:
            #return ProductForm
            return NgProductForm

    def get_context_data(self, **kwargs):
        context = super(UpdateProduct, self).get_context_data(**kwargs)
        context['lugati_editing'] = True
        return context

    def get_initial(self):
        res = {}
        #if self.kwargs['node_type'] == 'category':
        #    res['is_category'] = True
        res['price'] = self.object.get_price()
        res['bestseller'] = Bestseller.objects.filter(product=self.object).exists()
        res['id'] = self.object.id
        sp_offer = None
        try:
            sp_offer = SpecialOffer.objects.get(product=self.object)
        except:
            sp_offer = None
        if sp_offer:
            res['is_promo'] = True
            #res['is_promo'] = properties.is_promo(self.object)
        #res['is_product_of_the_month'] = properties.is_product_of_the_month(self.object)
        res['pic_array'] = ''
        #imgs = self.object.get_images()
        #for img in imgs:
        #    res['pic_array'] += str(img.id) + ';'

        return res

    def form_invalid(self, form):
        if self.request.is_ajax():
            res_dt = {
                'error': True
            }
            return HttpResponse(json.dumps(res_dt))
    def form_valid(self, form):
        self.object = form.save()
        pic_id_str = form.cleaned_data['pic_array']
        pic_id_array = pic_id_str.split(';')

        main_pic_set = False
        new_main_pic = False
        main_pic_id = ''
        if form.cleaned_data['main_image'] <> '':
            main_pic_set = True
            if (form.cleaned_data['main_image'].split('_')[0] == 'new'):
                new_main_pic = True
            main_pic_id = form.cleaned_data['main_image'].split('_')[1]

        for pic_id in pic_id_array:
            if pic_id <> '':
                tb_image = None
                try:
                    tb_image = ThebloqImage.objects.get(id=pic_id)
                    tb_image.content_object = self.object
                    tb_image.save()
                except:
                    logger.info('image with id ' + str(pic_id) + " doesn't exists")
                if tb_image:
                    if new_main_pic and (main_pic_id == pic_id):
                        self.object.main_image = tb_image


        if (not new_main_pic) and (main_pic_set):
            self.object.main_image = ThebloqImage.objects.get(pk=main_pic_id)

        if not self.object.is_category:
            self.object.setPrice(form.cleaned_data['price'])

            if form.cleaned_data['is_promo']:
                try:
                    sp_offer = SpecialOffer.objects.get(pk=self.object)
                except:
                    sp_offer = SpecialOffer()
                    sp_offer.product = self.object
                    sp_offer.save()
            else:
                SpecialOffer.objects.filter(product=self.object).delete()

            #properties.set_promo(form.cleaned_data['is_promo'], self.object)
            #properties.set_as_product_of_the_month(form.cleaned_data['is_product_of_the_month'], self.object)

            if form.cleaned_data['bestseller']:
                if not Bestseller.objects.filter(product=self.object).exists():
                    bestseller = Bestseller()
                    bestseller.product = self.object
                    bestseller.save()
            else:
                Bestseller.objects.filter(product=self.object).delete()

        if self.request.is_ajax():
            res_dt = {
                'error': False
            }
            return HttpResponse(json.dumps(res_dt))
        else:
            return super(UpdateProduct, self).form_valid(form)


class DeleteProduct(DeleteView):
    model = Product
    success_url = '/lugati_admin/'

#brands

def get_brands_control_panel(request):
    return render(request, 'lugati_admin/products/products_brands_panel.html')

def get_brands_tree(request):
    cur_site = get_current_site(request)
    cur_profile = LugatiUserProfile.objects.get(user=request.user)
    def get_brands_tree_internal(parent_object=None, level=0):
        dt = []
        brands = Brand.objects.all()
        for brand in brands:
            cur_node = {
                'label': brand.name,
                'uid': brand.id,
                'data': {
                    'definition': brand.name
                }
            }
            dt.append(cur_node)
        return dt
    res_dt = get_brands_tree_internal()
    return HttpResponse(json.dumps(res_dt))


class CreateBrand(CreateView):
    model = Brand
    template_name = 'products/create_brand.html'
    success_url = '/lugati_admin/#/brands'

    #def get_form_class(self):
    #    if self.kwargs['node_type'] == 'product':
    #        return ProductForm
    #    else:
    #        return CategoryForm

    #def get_initial(self):
    #    res = {}
    #
    #    return res

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
        else:
            return super(CreateBrand, self).form_valid(form)


class UpdateBrand(UpdateView):
    model = Brand
    template_name = 'products/edit_brand.html'
    success_url = '/lugati_admin/#/brands'

    #def get_form_class(self):
    #    if self.object.is_category:
    #        return CategoryForm
    #    else:
    #        return ProductForm

    def get_context_data(self, **kwargs):
        context = super(UpdateBrand, self).get_context_data(**kwargs)
        context['lugati_editing'] = True
        return context

    #def get_initial(self):
    #    res = {}
    #    return res

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
        else:
            return super(UpdateBrand, self).form_valid(form)

def get_brands_control_panel(request):
    return render(request, 'products/brands_control_panel.html')