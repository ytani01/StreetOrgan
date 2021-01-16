import os
from setuptools import setup, find_packages


_NAME = 'storgan'
_VERSION = '0.2.1'
_AUTHOR = 'Yoichi Tanibayashi'
_EMAIL = 'yoichi@tanibayashi.jp'
_URL = 'https://github.com/ytani01/StreetOrgan/'


def read_requirements():
    """Parse requirements from requirements.txt."""
    reqs_path = os.path.join('.', 'requirements.txt')
    with open(reqs_path, 'r') as f:
        requirements = [line.rstrip() for line in f]
    return requirements


with open("README.md") as f:
    long_description = f.read()

setup(
    name=_NAME,
    version=_VERSION,
    description='Streat Organ Roll Book Maker',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=_AUTHOR,
    author_email=_EMAIL,
    url=_URL,
    license='MIT',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
    ],
    install_requires=read_requirements(),
    packages=find_packages(exclude=('tests', 'docs')),
    python_requires='>=3.7',
)
