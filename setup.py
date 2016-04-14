import os
from setuptools import setup

setup(
    name='mondo-python',
    version='0.0.2',
    packages=['mondo', 'tools'],
    url='https://github.com/gabalese/mondo-python',
    license='MIT',
    install_requires=[
        'python-dateutil==2.5.2',
        'requests==2.9.1',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    author='gabalese',
    author_email='gabriele@alese.it',
    description='Library to deal with the Mondo API'
)
