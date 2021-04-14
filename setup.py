"""
plone_exporter
----------------------

An Apache Traffic Server metrics exporter for Prometheus.  Uses the
stats_over_http plugin to translate JSON data into Prometheus format.

"""

from setuptools import find_packages
from setuptools import setup

setup(
    name='plone_exporter',
    version='0.4.0',
    author='Mauro Amico',
    description='Traffic Server metrics exporter for Prometheus',
    long_description=__doc__,
    license='Apache Software License 2.0',
    keywords='prometheus monitoring plone installation',
    test_suite='tests',
    packages=['plone_push_gateway_exporter'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            # 'plone_exporter=plone_exporter.__main__:main',
            'plone_push_gateway_exporter=plone_exporter.push:main',
        ],
    },
    package_data={
        # 'plone_exporter': ['metrics.yaml'],
    },
    install_requires=[
        'prometheus_client>=0.0.11',
        'pyyaml>=3.12',
        'requests>=2.0.0',
        'click',
        'psutil',
    ],
    tests_require=[
        "pytest",
        "mock"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking :: Monitoring',
        'License :: OSI Approved :: Apache Software License',
    ],
)