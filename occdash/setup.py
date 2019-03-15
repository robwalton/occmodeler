import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="occdash",
    version="0.0.1",
    author="Rob Walton",
    author_email="rob.walton@eng.ox.ac.uk",
    description="View and interact with causal graphs of occasions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/robwalton/occdash",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
