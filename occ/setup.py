from setuptools import setup, find_packages

with open("README", 'r') as f:
    long_description = f.read()

setup(
    name='occ',
    version='0.5',
    packages=find_packages(),
    url='',
    license='MIT',
    author='Rob Walton',
    author_email='',
    long_description=long_description,
    install_requires=[
        'plotly',
        'networkx',
        'pandas',
        'pyspike'
    ],  # external packages as dependencies

)
