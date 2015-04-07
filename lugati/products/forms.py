# -*- coding: utf-8 -*-
from django import forms
from .models import Product
from django.forms import Textarea, HiddenInput
from django.utils.translation import ugettext as _
from djangular.forms import NgFormValidationMixin, NgModelFormMixin, NgModelForm
from djangular.styling.bootstrap3.forms import Bootstrap3Form, Bootstrap3FormMixin
from django.conf import settings
from lugati.products.models import Brand
from django.contrib.sites.models import get_current_site
from lugati.lugati_registration.models import LugatiUserProfile
import decimal

class ProductForm(NgModelForm):
    pic_array = forms.CharField(required=False, widget=HiddenInput)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(ProductForm, self).__init__(*args, **kwargs)

        cur_site = get_current_site(request)

        if settings.LUGATI_SPLIT_CATALOG_BY_COMPANY:
            cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()
            self.fields['parent_object'].queryset = Product.objects.filter(site=cur_site).filter(is_category=True).filter(company=cur_company)
        else:
            self.fields['parent_object'].queryset = Product.objects.filter(site=cur_site).filter(is_category=True)

        if 'BRANDS' in settings.LUGATI_MODULES:
            self.fields['brand'].queryset = Brand.objects.filter(site=cur_site)
        else:
            self.fields['brand'].queryset = Brand.objects.none()

        self.fields['price'].required = False
        self.fields['price'].decimal_places = 2
        self.fields['is_category'].initial = False

        if settings.SHOP_TYPE == 'MPS':
            self.fields['description'].widget = forms.HiddenInput()
        else:
            self.fields['description'].widget = forms.Textarea(attrs={'ckeditor': 'editorOptions', 'ng-model': 'submit_data.description'})
            self.fields['additional_info'].widget = forms.Textarea(attrs={'ckeditor': 'editorOptions', 'ng-model': 'submit_data.additional_info'})

    class Meta:
        model = Product
        exclude = ('thumbnail', 'assigned_to')
        widgets = {
            'is_category': HiddenInput(),
            'company': HiddenInput(),
            'site': HiddenInput(),
            'active': forms.HiddenInput(),
            'styled_name': forms.HiddenInput(),
            'styled_description': forms.HiddenInput(),
            'code': forms.HiddenInput(),
            'sku': forms.HiddenInput(),
            'priority': forms.HiddenInput(),
            'price_wo_discount': HiddenInput(),
            # ~mps
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'preview': forms.Textarea(attrs={'class': 'form-control'}),
        }

class NgProductForm(NgModelFormMixin, NgFormValidationMixin, ProductForm, Bootstrap3FormMixin):
    form_name = "submit_data_form"
    scope_prefix = 'submit_data'

class NonscientificDecimalField(forms.DecimalField):
    """ Prevents values from being displayed with E notation, with trailing 0's
        after the decimal place  truncated. (This causes precision to be lost in
        many cases, but is more user friendly and consistent for non-scientist
        users)
    """
    def value_from_object(self, obj):
        def remove_exponent(val):
            """Remove exponent and trailing zeros.
               >>> remove_exponent(Decimal('5E+3'))
               Decimal('5000')
            """
            context = decimal.Context(prec=self.max_digits)
            return val.quantize(decimal.Decimal(1), context=context) if val == val.to_integral() else val.normalize(context)

        val = super(NonscientificDecimalField, self).value_from_object(obj)
        if isinstance(val, decimal.Decimal):
            return remove_exponent(val)

class ToppingForm(NgModelForm, Bootstrap3FormMixin):
    price = NonscientificDecimalField(required=False)
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(ToppingForm, self).__init__(*args, **kwargs)

        cur_site = get_current_site(request)

        if settings.LUGATI_SPLIT_CATALOG_BY_COMPANY:
            cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()
            self.fields['parent_object'].queryset = Product.objects.filter(site=cur_site).filter(is_category=True).filter(company=cur_company)
        else:
            self.fields['parent_object'].queryset = Product.objects.filter(site=cur_site).filter(is_category=True)

        if self.instance:
            if self.instance.price:
                self.fields['price'].initial = self.instance.price
            else:
                self.fields['price'].initial = 0

    class Meta:
        model = Product
        exclude = ( 'price',
                    'thumbnail',
                    'is_category',
                    'company',
                    'site',
                    'active',
                    'code',
                    'sku',
                    'priority',
                    'additional_info',
                    'price_wo_discount',
                    'additional_info',
                    'preview',
                    # 'parent_object',
                    'description',
                    'styled_name',
                    'styled_description',
                    'is_topping',
                    'brand',
                    'assigned_to')
        # topping_name = forms.CharField(max_length=200, min_length=1, label='Name')
        # price = forms.DecimalField()

class NgToppingForm(NgModelFormMixin, NgFormValidationMixin, ToppingForm):

    form_name = "submit_data_form"
    scope_prefix = 'submit_data'

class CategoryForm(NgModelForm):
    pic_array = forms.CharField(required=False, widget=HiddenInput)
    main_image = forms.CharField(required=False, widget=HiddenInput)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(CategoryForm, self).__init__(*args, **kwargs)

        cur_site = get_current_site(request)

        if settings.LUGATI_SPLIT_CATALOG_BY_COMPANY:
            cur_company = LugatiUserProfile.objects.get(user=request.user).get_company()
            self.fields['parent_object'].queryset=Product.objects.filter(site=cur_site).filter(is_category=True).filter(company=cur_company)
        else:
            self.fields['parent_object'].queryset=Product.objects.filter(site=cur_site).filter(is_category=True)

        self.fields['is_category'].initial = True

    class Meta:
        model = Product
        exclude = ('sku', 'thumbnail', 'brand', 'price_wo_discount', 'price', 'is_topping', 'assigned_to')

        widgets = {
            'is_category': HiddenInput(),
            'in_stock': HiddenInput(),
            'active': forms.HiddenInput(),
            'site': HiddenInput(),
            'description': forms.HiddenInput(),
            'code': forms.HiddenInput(),
            'name': forms.TextInput(),
            'preview': forms.HiddenInput(),
            'priority': forms.HiddenInput(),
            'company': forms.HiddenInput(),
            'additional_info': forms.HiddenInput(),
            'styled_name': forms.HiddenInput(),
            'styled_description': forms.HiddenInput(),
        }

class NgCategoryForm(NgModelFormMixin, NgFormValidationMixin, CategoryForm, Bootstrap3FormMixin):
    form_name = "submit_data_form"
    scope_prefix = 'submit_data'
