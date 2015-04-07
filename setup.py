#!/usr/bin/env python
#coding: utf-8
__author__ = 'xors'

from distutils.core import setup
import sys

reload(sys).setdefaultencoding("UTF-8")

setup(
    name='lugati',
    version='0.1.2',
    author='Sergey Grigorev',
    author_email='dev@lugati.ru',
    packages=[
        'lugati', 'lugati.lugati_admin',
        'lugati.lugati_feedback',
        'lugati.lugati_media', 'lugati.lugati_media.lugati_gallery',
        'lugati.lugati_mobile', 'lugati.lugati_payment',
        'lugati.lugati_payment.lugati_coinbase', 'lugati.lugati_payment.lugati_mycelium',
        'lugati.lugati_payment.lugati_robokassa', 'lugati.lugati_payment.lugati_stripe',
        'lugati.lugati_points_of_sale', 'lugati.lugati_registration',
        'lugati.lugati_shop', 'lugati.lugati_shop.lugati_cart',
        'lugati.lugati_shop.lugati_delivery', 'lugati.lugati_shop.lugati_orders',
        'lugati.lugati_shop.lugati_pricelist', 'lugati.lugati_shop.lugati_promo',
        'lugati.lugati_shop.lugati_reports', 'lugati.lugati_static',
        'lugati.lugati_widgets', 'lugati.products',
    ],
    url='http://lugati.ru',
    download_url = 'https://github.com/xorsnn/lugati/zipball/master',
    license = 'MIT license',
    description = u'Основные процедуры и функции lugati_cms.'.encode('utf8'),
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Russian',
    )
)