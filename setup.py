"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/Livefyre/dns-kit
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from os import path

setup(
    name='dns-kit',
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.9',
    description='Tools for managing DNS zones',
    # The project's main homepage.
    url='https://github.com/Livefyre/dns-kit',

    # Author details
    author='Nicholas Fowler',
    author_email='nfowler@livefyre.com',

    # What does your project relate to?
    keywords='dns route53 aws bindlite',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['dns_kit'],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['py-yacc','boto','docopt','safeoutput','moto'],
    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'dns_kit': ['app.yaml'],
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'bindlite2route53=dns_kit.bindlite2route53:main',
            'route53dump=dns_kit.route53dump:main',
            'route53diff=dns_kit.route53diff:main',
            'push2route53=dns_kit.push2route53:main',
            'filter_bindlite=dns_kit.filter_bindlite:main',
            'merge_bindlite=dns_kit.merge_bindlite:main',
            'bindlite_lookup=dns_kit.bindlite_lookup:main',
        ],
    },
)
