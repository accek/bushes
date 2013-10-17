# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='bushes',
    version = '0.1.dev',
    description='Dependency tree annotation tool',
    author='Szymon Acedański',
    author_email='accek@mimuw.edu.pl',
    url='http://sio2project.mimuw.edu.pl',
    install_requires=[
        "Django>=1.5",
        "pytz>=2013b",
        "South",
        "django-registration>=1.0",
        "django-debug-toolbar",
        "django-extensions",
        "django-bootstrap3",
        "django-htmlmin",
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
)
