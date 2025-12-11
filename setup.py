# setup.py (nella radice del repository)
from setuptools import setup, find_packages

setup(
    name="openstack-forecasting-plugin",
    version="2.0.0",
    description="AI Resource Forecasting Plugin for OpenStack",
    author="Il Tuo Nome",
    author_email="tua@email.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask>=2.0.0',
        'numpy>=1.21.0',
        'openstacksdk>=0.61.0',
    ],
    entry_points={
        'console_scripts': [
            'forecasting-api = forecasting_plugin.api:main',
        ],
    },
)