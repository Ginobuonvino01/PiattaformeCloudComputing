from setuptools import setup, find_packages

setup(
    name="openstack-forecasting-plugin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'flask>=2.0.0',
        'numpy>=1.21.0',
        'pandas>=1.3.0',
        'scikit-learn>=1.0.0',
        'openstacksdk>=0.61.0',
    ],
    entry_points={
        'console_scripts': [
            'forecasting-service=forecasting_plugin.api:main',
        ],
    },
)