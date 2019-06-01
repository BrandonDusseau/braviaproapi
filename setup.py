import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-bravia-pro-api",
    version="0.0.1",
    author="Brandon Dusseau",
    author_email="brandon.dusseau@gmail.com",
    description="Library for communicating with Sony Bravia TVs utilizing its Bravia Professional API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BrandonDusseau/py-bravia-pro-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
