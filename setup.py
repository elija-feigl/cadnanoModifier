import sys

from setuptools import find_packages, setup

from cadnano_modifier.version import get_version

""" Modification of DNA Origami nano structure designed with caDNAno."""

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("LICENSE", "r") as fh:
    license = fh.read()

v_python = sys.version_info
if (v_python.major <= 3) and (v_python.minor <= 7):
    sys.exit('Sorry, Python < 3.7.0 is not supported')

setup(
    name="cadnano_modifier",
    python_requires=">=3.7.0",
    version=get_version(),
    author="Elija Feigl",
    author_email="elija.feigl@tum.de",
    description=__doc__,
    license=license,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elija-feigl/cadnanoModifier",
    packages=find_packages(),
    include_package_data=True,
    install_requires=(
        'click <= 7',
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GNU General Public License Version 3",
        "Operating System :: OS Independent",
    ],
    entry_points='''
        [console_scripts]
        cadnanoModifier=cadnano_modifier.scripts.modify:cli
    ''',
)
