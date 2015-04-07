__author__ = 'xors'
from django.core.urlresolvers import resolve
from django.contrib.contenttypes.models import ContentType
from lugati.lugati_registration.models import LugatiUserProfile
from lugati.lugati_media.models import ThebloqImage
import os
from urlparse import urlparse
import requests
from django.core.files import File

def get_content_type_id_by_name(model_name):
    if model_name.lower() == 'Product'.lower():
        from lugati.products.models import Product
        return ContentType.objects.get_for_model(Product).id
    elif model_name.lower() == 'LugatiSlider'.lower():
        from lugati.lugati_media.lugati_gallery.models import LugatiSlider
        return ContentType.objects.get_for_model(LugatiSlider).id
    elif model_name.lower() == 'ShoppingPlace'.lower():
        from lugati.lugati_shop.models import ShoppingPlace
        return ContentType.objects.get_for_model(ShoppingPlace).id
    elif model_name.lower() == 'SalesPoint'.lower():
        from lugati.lugati_points_of_sale.models import SalesPoint
        return ContentType.objects.get_for_model(SalesPoint).id
    elif model_name.lower() == 'City'.lower():
        from lugati.lugati_points_of_sale.models import City
        return ContentType.objects.get_for_model(City).id
    elif model_name.lower() == 'DeliveryOption'.lower():
        from lugati.lugati_shop.lugati_delivery.models import DeliveryOption
        return ContentType.objects.get_for_model(DeliveryOption).id
    elif model_name.lower() == 'DeliveryPrice'.lower():
        from lugati.lugati_shop.lugati_delivery.models import DeliveryPrice
        return ContentType.objects.get_for_model(DeliveryPrice).id
    elif model_name.lower() == 'Order'.lower():
        from lugati.lugati_shop.lugati_orders.models import Order
        return ContentType.objects.get_for_model(Order).id
    elif model_name.lower() == 'GalleryItem'.lower():
        from lugati.lugati_media.lugati_gallery.models import GalleryItem
        return ContentType.objects.get_for_model(GalleryItem).id
    elif model_name.lower() == 'ThebloqVideo'.lower():
        from lugati.lugati_media.models import ThebloqVideo
        return ContentType.objects.get_for_model(ThebloqVideo).id
    elif model_name.lower() == 'LugatiTextBlock'.lower():
        from lugati.lugati_widgets.models import LugatiTextBlock
        return ContentType.objects.get_for_model(LugatiTextBlock).id
    elif model_name.lower() == 'Shop'.lower():
        from lugati.lugati_shop.models import Shop
        return ContentType.objects.get_for_model(Shop).id
    elif model_name.lower() == 'ShoppingPlace'.lower():
        from lugati.lugati_shop.models import ShoppingPlace
        return ContentType.objects.get_for_model(ShoppingPlace).id
    elif model_name.lower() == 'LugatiDevice'.lower():
        from lugati.lugati_mobile.models import LugatiDevice
        return ContentType.objects.get_for_model(LugatiDevice).id
    elif model_name.lower() == 'LugatiClerk'.lower():
        from lugati.lugati_shop.models import LugatiClerk
        return ContentType.objects.get_for_model(LugatiClerk).id
    elif model_name.lower() == 'LugatiPoem'.lower():
        from lugati.lugati_widgets.models import LugatiPoem
        return ContentType.objects.get_for_model(LugatiPoem).id
    elif model_name.lower() == 'LugatiNews'.lower():
        from lugati.lugati_widgets.models import LugatiNews
        return ContentType.objects.get_for_model(LugatiNews).id
    elif model_name.lower() == 'LugatiCompany'.lower():
        from lugati.lugati_shop.models import LugatiCompany
        return ContentType.objects.get_for_model(LugatiCompany).id
    elif model_name.lower() == 'LugatiPortfolioItem'.lower():
        from lugati.lugati_widgets.models import LugatiPortfolioItem
        return ContentType.objects.get_for_model(LugatiPortfolioItem).id
    else:
        return ''


def can_create(content_type):
    if content_type.model_class().__name__ == 'Shop':
        return True
    elif content_type.model_class().__name__ == 'LugatiDevice':
        return False
    elif content_type.model_class().__name__ == 'Order':
        return False
    elif content_type.model_class().__name__ == 'LugatiCompany':
        return False
    else:
        return True

def can_delete(content_type):
    if content_type.model_class().__name__ == 'Shop':
        return True
    if content_type.model_class().__name__ == 'Order':
        return True
    elif content_type.model_class().__name__ == 'LugatiCompany':
        return False
    else:
        return True

def is_hierarchical(content_type):
    if content_type.model_class().__name__ == 'Product':
        return True
    if content_type.model_class().__name__ == 'City':
        return True
    else:
        return False

def has_images(content_type):
    if content_type.model_class().__name__ == 'Product':
        return True
    elif content_type.model_class().__name__ == 'GalleryItem':
        return True
    elif content_type.model_class().__name__ == 'LugatiCompany':
        return True
    # elif content_type.model_class().__name__ == 'Shop':
    #     return True
    elif content_type.model_class().__name__ == 'LugatiPoem':
        return True
    elif content_type.model_class().__name__ == 'ThebloqVideo':
        return True
    elif content_type.model_class().__name__ == 'LugatiPortfolioItem':
        return True
    elif content_type.model_class().__name__ == 'LugatiClerk':
        return True
    else:
        return False

def has_map(content_type):
    if content_type.model_class().__name__ == 'SalesPoint':
        return True
    elif content_type.model_class().__name__ == 'City':
        return True
    else:
        return False

def get_ids(request, path= None):

    if path:
        match = resolve(path)
    else:
        match = resolve(request.path)

    prod_id = ''
    cat_id = ''

    if 'prod_id' in match.kwargs:
        prod_id = match.kwargs['prod_id']
    if 'cat_id' in match.kwargs:
        cat_id = match.kwargs['cat_id']

    if cat_id == '':
        if 'cat_id' in request.GET:
            cat_id = request.GET['cat_id']
        #deprecated
        if cat_id == '':
            if 'parent_product' in request.GET:
                cat_id = request.GET['parent_product']
        #deprecated

    if prod_id == '':
        if 'prod_id' in request.GET:
            prod_id = request.GET['prod_id']

        #deprecated
        if prod_id == '':
            if 'product_id' in request.GET:
                cat_id = request.GET['product_id']
        #deprecated

    return cat_id, prod_id

def get_user_profile(user):
    return LugatiUserProfile.objects.get(user=user)

def get_object_images(obj):
    return ThebloqImage.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj.__class__))

def download_image(img_url):
    tb_image = ThebloqImage()
    file_save_dir = 'static/upload'
    filename = urlparse(img_url).path.split('/')[-1]
    r = requests.get(img_url)
    with open(os.path.join(file_save_dir, filename), 'wb') as f:
        f.write(r.content)
    tb_image.file = File(open(os.path.join(file_save_dir, filename)))
    tb_image.save()
    return tb_image