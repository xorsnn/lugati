from django.conf.urls import patterns, include, url
from lugati.products.models import Product, ProductPropertyValue
from django.contrib.contenttypes.models import ContentType
from lugati.lugati_media.models import ThebloqImage
from lugati.lugati_admin.models import Tooltip
from lugati.lugati_shop.lugati_orders.models import Order
from lugati.lugati_shop.models import ShoppingPlace
from django.contrib.flatpages.models import FlatPage

urlpatterns = patterns('',
    url(r'^request_test$', 'lugati.views.request_test', name='request_test'),

    #url(r'^callbacks/', include('lugati.lugati_callbacks.urls', namespace='callbacks')),
    url(r'^delete_product/(?P<object_id>\w+)/$', 'lugati.views.api_delete_object', {'content_object_id': str(ContentType.objects.get_for_model(Product).id)}, name='api_delete_object'),
    url(r'^delete_object/(?P<content_type_id>\w+)/(?P<object_id>\w+)/$', 'lugati.views.api_delete_object', name='api_delete_object'),

    url(r'^send_via_email/(?P<content_type_id>\w+)/(?P<object_id>\w+)/$', 'lugati.views.send_via_email', name='send_via_email'),

    # url(r'^orders$', 'lugati.lugati_shop.lugati_orders.views.api_orders', name='api_orders'),

    url(r'^lugati_content_type/(?P<id>\w+)', 'lugati.views.lugati_content_type', name='lugati_content_type'),
    url(r'^lugati_content_type/$', 'lugati.views.lugati_content_type', name='lugati_content_type'),


#universal api
    # url(r'^category_tree/(?P<content_object_id>\w+)/$', 'lugati.views.category_tree', name='category_tree'),
    #url(r'^(?P<content_object_id>\w+)$', 'lugati.views.api_objects', name='api_objects'),
#~universal api



    url(r'^brands$', 'lugati.products.views.api_brands', name='api_brands'),
    url(r'^brands/(?P<id>\w+)$', 'lugati.products.views.api_brands', name='api_brands'),

    url(r'^video$', 'lugati.lugati_media.views.api_video', name='api_video'),
    url(r'^video/(?P<id>\w+)/$', 'lugati.lugati_media.views.api_video', name='api_video'),


    url(r'^cart_item$', 'lugati.lugati_shop.lugati_cart.views.api_cart_items', name='api_cart_items'),
    url(r'^cart_item/(?P<cart_item_id>\w+)$', 'lugati.lugati_shop.lugati_cart.views.api_cart_items', name='api_cart_items'),
    url(r'^cart_item/(?P<cart_item_id>\w+)/$', 'lugati.lugati_shop.lugati_cart.views.api_cart_items', name='api_cart_items'),

    url(r'^devices/$', 'lugati.lugati_mobile.views.api_devices', name='api_devices'),
    #exchange
    url(r'^trading/order/$', 'lugati.lugati_exchange.views.api_order', name='api_order'),

    url(r'^images$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(ThebloqImage).id)}, name='api_objects'),
    url(r'^images/(?P<object_id>\w+)$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(ThebloqImage).id)}, name='api_objects'),
    url(r'^images/(?P<object_id>\w+)/$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(ThebloqImage).id)}, name='api_objects'),

    url(r'^order_points$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(ShoppingPlace).id)}, name='api_objects'),

    # url(r'^products$', 'lugati.products.views.api_products', name='api_products'),
    url(r'^products$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(Product).id)}, name='api_objects'),
    url(r'^products/(?P<object_id>\w+)$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(Product).id)}, name='api_objects'),
    url(r'^products/(?P<object_id>\w+)/$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(Product).id)}, name='api_objects'),
    url(r'^products/(?P<id>\w+)/(?P<brand_id>\w+)/$', 'lugati.products.views.api_products', name='api_products'),
    # url(r'^' + str(ContentType.objects.get_for_model(Product).id) + '$', 'lugati.products.views.api_products', name='api_products'),
    url(r'^' + str(ContentType.objects.get_for_model(Product).id) + '$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(Product).id)}, name='api_products'),

    url(r'^tooltips/(?P<object_id>\w+)$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(Tooltip).id)}, name='api_objects'),
    url(r'^tooltips/(?P<object_id>\w+)/$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(Tooltip).id)}, name='api_objects'),

    url(r'^orders$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(Order).id)}, name='api_objects'),
    url(r'^orders/(?P<object_id>\w+)$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(Order).id)}, name='api_objects'),
    url(r'^orders/(?P<object_id>\w+)/$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(Order).id)}, name='api_objects'),

    url(r'^product_option$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(ProductPropertyValue).id)}, name='api_objects'),
    url(r'^product_option/(?P<object_id>\w+)$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(ProductPropertyValue).id)}, name='api_objects'),
    url(r'^product_option/(?P<object_id>\w+)/$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(ProductPropertyValue).id)}, name='api_objects'),

#flatpages
    url(r'^flat_page/(?P<object_id>\w+)$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(FlatPage).id)}, name='api_objects'),
    url(r'^flat_page/(?P<object_id>\w+)/$', 'lugati.views.api_objects', {'content_object_id': str(ContentType.objects.get_for_model(FlatPage).id)}, name='api_objects'),

    url(r'^(?P<content_object_id>\w+)$', 'lugati.views.api_objects', name='api_objects'),
    url(r'^(?P<content_object_id>\w+)/$', 'lugati.views.api_objects', name='api_objects'),
    url(r'^(?P<content_object_id>\w+)/(?P<object_id>\w+)$', 'lugati.views.api_objects', name='api_objects'),
    url(r'^(?P<content_object_id>\w+)/(?P<object_id>\w+)/$', 'lugati.views.api_objects', name='api_objects'),


)
