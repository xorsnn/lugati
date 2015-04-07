from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
# company
    url(r'^get_company_title/(?P<title_id>\w+)/$', 'lugati.lugati_shop.views.get_company_title', name='get_company_title'),
# ~company

    url(r'^send_tracking_number/$', 'lugati.lugati_shop.views.send_tracking_number', name='send_tracking_number'),

    url(r'^clear_cart/$', 'lugati.lugati_shop.views.clear_cart', name='clear_cart'),

    url(r'^single_order_point_qr_code/(?P<object_id>\w+)/$', 'lugati.lugati_shop.views.single_order_point_qr_code', name='single_order_point_qr_code'),
    url(r'^generate_order_points_stickers/$', 'lugati.lugati_shop.views.generate_order_points_stickers', name='generate_order_points_stickers'),
    #url(r'^generate_order_points_stickers/(?P<object_id>\w+)/$', 'lugati.lugati_shop.views.generate_order_points_stickers', name='generate_order_points_stickers'),

    url(r'^pdf_order_points_stickers/$', 'lugati.lugati_shop.views.pdf_order_points_stickers', name='pdf_order_points_stickers'),
    url(r'^pdf_order_points_stickers/(?P<col_num>\w+)/$', 'lugati.lugati_shop.views.pdf_order_points_stickers', name='pdf_order_points_stickers'),
    # url(r'^pdf_order_points_stickers_test/$', 'lugati.lugati_shop.views.pdf_order_points_stickers_test', name='pdf_order_points_stickers_test'),

# demo
    url(r'^load_demo_data/$', 'lugati.lugati_shop.views.load_demo_data', name='load_demo_data'),
    url(r'^generate_demo_order_points/$', 'lugati.lugati_shop.views.generate_demo_order_points', name='generate_demo_order_points'),
    url(r'^generate_demo_inventory/$', 'lugati.lugati_shop.views.generate_demo_inventory', name='generate_demo_inventory'),
    url(r'^generate_demo_sales/$', 'lugati.lugati_shop.views.generate_demo_sales', name='generate_demo_sales'),

    url(r'^generate_order_points/$', 'lugati.lugati_shop.views.generate_order_points', name='generate_order_points'),
    url(r'^change_company_data/$', 'lugati.lugati_shop.views.change_company_data', name='change_company_data'),
# ~demo


    url(r'^ng_crop_image_template/(?P<content_object_id>\w+)/(?P<object_id>\w+)/(?P<image_id>\w+)/$', 'lugati.lugati_shop.views.ng_crop_image_template', name='ng_crop_image_template'),

    url(r'^lugati_cart/', include('lugati.lugati_shop.lugati_cart.urls', namespace='lugati_cart')),

    url(r'^lugati_reports/', include('lugati.lugati_shop.lugati_reports.urls', namespace='lugati_reports')),

    url(r'^clerk_login/$', 'lugati.lugati_shop.views.clerk_login', name='clerk_login'),
    url(r'^lugati_call/$', 'lugati.lugati_shop.views.lugati_call', name='lugati_call'),

    url(r'^lugati_test_pay/$', 'lugati.lugati_shop.views.lugati_test_pay', name='lugati_test_pay'),

    #poses MPS!!
    url(r'^point_of_sale/(?P<pos_id>\w+)/$', 'lugati.lugati_shop.views.pos_catalog', name='pos_catalog'),
    url(r'^point_of_sale/start/(?P<pos_id>\w+)/$', 'lugati.lugati_shop.views.pos_catalog_start', name='pos_catalog_start'),
    #~poses

    url(r'^lugati_delivery/', include('lugati.lugati_shop.lugati_delivery.urls', namespace='lugati_delivery')),
    url(r'^lugati_pricelists/', include('lugati.lugati_shop.lugati_pricelist.urls', namespace='lugati_pricelists')),
    url(r'^lugati_orders/', include('lugati.lugati_shop.lugati_orders.urls', namespace='lugati_orders')),
    #deprecated
    url(r'^add_product/$', 'lugati.lugati_shop.views.add_product', name='lugati_remove_product'),
    url(r'^remove_product/$', 'lugati.lugati_shop.views.remove_product', name='lugati_remove_product'),
    #~deprecated
    url(r'^add_product_to_cart/$', 'lugati.lugati_shop.views.add_product_to_cart', name='add_product_to_cart'),
    url(r'^remove_product_from_cart/$', 'lugati.lugati_shop.views.remove_product_from_cart', name='remove_product_from_cart'),

    url(r'^get_cart_items/$', 'lugati.lugati_shop.views.get_cart_items', name='get_cart_items'),
    # url(r'^get_catalog_items/$', 'lugati.lugati_shop.views.get_catalog_items', name='get_catalog_items'),

    #API

    #--template
    url(r'^lugati_get_payment_template/$', 'lugati.lugati_shop.views.lugati_get_payment_template', name='lugati_get_payment_template'),
    url(r'^lugati_get_success_payment_template/$', 'lugati.lugati_shop.views.lugati_get_success_payment_template', name='lugati_get_success_payment_template'),
    url(r'^lugati_get_catalog_template/$', 'lugati.lugati_shop.views.lugati_get_catalog_template', name='lugati_get_catalog_template'),
    # url(r'^lugati_get_cart_template/$', 'lugati.lugati_shop.views.lugati_get_cart_template', name='lugati_get_cart_template'),
    url(r'^lugati_get_cart_base_template/$', 'lugati.lugati_shop.views.lugati_get_cart_base_template', name='lugati_get_cart_base_template'),



    url(r'^get_ng_catalog_template/$', 'lugati.lugati_shop.views.get_ng_catalog_template', name='get_ng_catalog_template'),
    url(r'^get_ng_product_details_template/$', 'lugati.lugati_shop.views.get_ng_product_details_template', name='get_ng_product_details_template'),
    url(r'^get_ng_cart_template/$', 'lugati.lugati_shop.views.get_ng_cart_template', name='get_ng_cart_template'),

    #~~template
    url(r'^lugati_get_catalog_items/$', 'lugati.lugati_shop.views.lugati_get_catalog_items', name='lugati_get_catalog_items'),


    #~API
    url(r'^get_product_details/$', 'lugati.lugati_shop.views.get_product_details', name='get_product_details'),
    url(r'^get_product_thumbnail/$', 'lugati.lugati_shop.views.get_product_thumbnail', name='get_product_thumbnail'),


    url(r'^confirm_order/$', 'lugati.lugati_shop.views.confirm_order', name='lugati_confirm_order'),
    #url(r'^cart/$', 'lugati.lugati_shop.views.show_cart', name='lugati_shopping_cart'),

    url(r'^cart/$', 'lugati.lugati_shop.views.shopping_cart', name='lugati_shopping_cart'),

    url(r'^(?P<cat_id>\w+)/$', 'lugati.lugati_shop.views.catalog', name='catalog_page'),
    #url(r'^(?P<cat_id>\w+)/(?P<prod_id>\w+)/$', 'lugati.lugati_shop.views.catalog', name='catalog_page'),
    url(r'^product_details/(?P<prod_id>\w+)/$', 'lugati.lugati_shop.views.product_details', name='product_details'),

    url(r'^$', 'lugati.lugati_shop.views.catalog', name='catalog_page'),
)
