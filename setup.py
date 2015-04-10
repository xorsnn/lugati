#!/usr/bin/env python
#coding: utf-8
__author__ = 'xors'
from setuptools import setup, find_packages
# from distutils.core import setup
import sys

reload(sys).setdefaultencoding("UTF-8")

setup(
    name='lugati',
    version='0.1.5',
    author='Sergey Grigorev',
    author_email='dev@lugati.ru',
    packages=find_packages(),
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