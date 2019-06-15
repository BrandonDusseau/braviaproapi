import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="braviaproapi",
    version="0.0.1",
    author="Brandon Dusseau",
    author_email="brandon.dusseau@gmail.com",
    description="Library for communicating with Sony Bravia TVs utilizing its Bravia Professional API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BrandonDusseau/py-bravia-pro-api",
    packages=setuptools.find_packages(exclude=["http"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    install_requires=["requests", "python-dateutil", "packaging", "pycryptodome", "M2Crypto"],
    keywords='sony bravia television remote control library'
)
