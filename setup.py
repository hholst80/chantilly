from setuptools import find_packages, setup

setup(
    name='chantilly',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'creme>=0.5.0',
        'dill==0.3.1.1',
        'flask==1.1.1',
        'influxdb==5.2.3'
    ],
    extras_require={
        'dev': [
            'mypy>=0.770',
            'pytest>=5.3.5'
        ]
    },
    entry_points={
        'console_scripts': [
            'chantilly=app:cli_hook'
        ],
    },
)
