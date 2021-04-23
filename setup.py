"""
prometheus_plone_exporter
----------------------

"""

from setuptools import find_packages
from setuptools import setup

setup(
    name='plone_push_gateway_exporter',
    version='0.0.1',
    author='Mauro Amico',
    description='Plone buildout metrics exporter for Prometheus',
    long_description=__doc__,
    license='Apache Software License 2.0',
    keywords='prometheus monitoring plone installation',
    test_suite='tests',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            # 'plone_exporter=plone_exporter.__main__:main',
            'plone_push_gateway_exporter=prometheus_plone_exporter.push:main',
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
