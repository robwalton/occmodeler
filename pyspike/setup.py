from setuptools import setup, find_packages

with open("README", 'r') as f:
    long_description = f.read()

setup(
    name='pyspike',
    version='0.5',
    packages=find_packages(),
    url='',
    license='MIT',
    author='Rob Walton',
    author_email='',
    long_description=long_description,
    install_requires=[
        'colorlover',
        'networkx',
        'pandas'
    ],  # external packages as dependencies

)
