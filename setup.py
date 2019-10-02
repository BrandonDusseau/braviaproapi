import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="braviaproapi",
    version="0.9.0",
    author="Brandon Dusseau",
    author_email="brandon.dusseau+pypi@gmail.com",
    description="Library for controlling Sony Bravia TVs utilizing their Bravia Professional API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BrandonDusseau/py-bravia-pro-api",
    packages=setuptools.find_packages(exclude=["http"]),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent ",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    install_requires=[
        "requests>=2,<3",
        "python-dateutil>=2,<3",
        "packaging>=19",
        "pycryptodome>=3,<4"
    ],
    keywords='sony bravia television remote control library'
)
