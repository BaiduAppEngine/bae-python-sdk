# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "bae_memcache",
    version = "1.0.0",
    packages = find_packages(),
    package_data = {
        'bae_memcache': ['*.so']    
    },
    install_requires = ['bae_utils'],
    author = "bae",
    description = 'bae memcache sdk',
)
