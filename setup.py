# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.rst')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')

setup(
    long_description=readme,
    name='fast-soup',
    version='1.1.0',
    description='BeautifulSoup interface for lxml',
    python_requires='==3.*,>=3.6.0',
    author='spumer',
    author_email='spumer-tm@yandex.ru',
    license='MIT',
    packages=['fast_soup'],
    package_dir={"": "."},
    package_data={},
    install_requires=[
        'beautifulsoup4==4.*,>=4.3.2', 'cssselect==1.*,>=1.0.1',
        'lxml==4.*,>=4.5.0'
    ],
    extras_require={
        "dev": [
            "black==19.*,>=19.10.0", "bumpversion==0.*,>=0.5.3",
            "flake8-awesome==1.*,>=1.2.0", "pytest>=5,<8",
            "pytest-cov>=2,<5", "pytest-deadfixtures==2.*,>=2.1.0",
            "unify==0.*,>=0.5.0"
        ]
    },
)
