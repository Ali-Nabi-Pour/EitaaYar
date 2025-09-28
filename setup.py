from setuptools import setup, find_packages
import codecs
import os

# خواندن محتوای فایل README
here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

setup(
    name="EitaaYar",
    version="1.0",
    author="Ali NabiPour",
    author_email="noyan.joun.89@gmail.com",
    description="A comprehensive Python client for EitaaYar.ir API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ali-Nabi-Pour/Eitaayar",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp>=3.8.0",
        "requests>=2.28.0",
    ],
    keywords="eitaayar, eitaa, api, client, bot, messaging, iran",
    project_urls={
        "Homepage": "https://github.com/Ali-Nabi-Pour/Eitaayar",
        "Bug Reports": "https://github.com/Ali-Nabi-Pour/Eitaayar/issues",
        "Source": "https://github.com/Ali-Nabi-Pour/Eitaayar",
    },
)
