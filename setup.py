import os
from setuptools import setup

setup(
    name='mondo-python',
    version='0.0.2',
    packages=['mondo', 'tools'],
    url='https://github.com/gabalese/mondo-python',
    license='MIT',
    install_requires=[
        'appnope==0.1.0',
        'cookies==2.2.1',
        'decorator==4.0.9',
        'gnureadline==6.3.3',
        'nose==1.3.7',
        'path.py==8.1.2',
        'pexpect==4.0.1',
        'pickleshare==0.6',
        'ptyprocess==0.5.1',
        'py==1.4.31',
        'pytest==2.9.1',
        'python-dateutil==2.5.2',
        'requests==2.9.1',
        'responses==0.5.1',
        'simplegeneric==0.8.1',
        'six==1.10.0',
        'traitlets==4.2.1',
        'wheel==0.24.0',
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
