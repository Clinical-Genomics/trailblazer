"""
Trailblazer is a tool to manage and track state of analyses.

You can install it from PyPI as follows::
    pip install trailblazer

For more detailed instructions, run :code:`trailblazer --help`

See the GitHub repo for documentation:
`Clinical-Genomics/analysis <https://github.com/Clinical-Genomics/analysis>`_
"""

import codecs
import io
import os

# Always prefer setuptools over distutils
from setuptools import find_packages, setup

AUTHOR = "henrik.stranneheim"
DESCRIPTION = "Trailblazer is a tool to manage and track state of analyses"
EMAIL = "henrik.stranneheim@scilifelab.se"
HERE = os.path.abspath(os.path.dirname(__file__))
NAME = "trailblazer"


def parse_reqs(req_path="./requirements.txt"):
    """Recursively parse requirements from nested pip files"""
    install_requires = []
    with codecs.open(req_path, "r") as handle:
        # remove comments and empty lines
        lines = (line.strip() for line in handle if line.strip() and not line.startswith("#"))
        for line in lines:
            # check for nested requirements files
            if line.startswith("-r"):
                # recursively call this function
                install_requires += parse_reqs(req_path=line[3:])
            else:
                # add the line as a new requirement
                install_requires.append(line)
    return install_requires


# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
        LONG_DESCRIPTION = "\n" + f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION


setup(
    name=NAME,
    version="19.0.14",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    keywords="analysis monitoring",
    author=AUTHOR,
    author_email=EMAIL,
    license="MIT",
    url="https://github.com/Clinical-Genomics/trailblazer",
    packages=find_packages(exclude=("tests*", "docs", "examples")),
    include_package_data=True,
    zip_safe=False,
    install_requires=parse_reqs(),
    tests_require=[
        "pytest",
    ],
    entry_points={
        "console_scripts": [
            "trailblazer = trailblazer.cli.core:base",
        ]
    },
    # See: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Environment :: Console",
    ],
)
