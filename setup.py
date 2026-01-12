#!/usr/bin/env python
"""
Setup script for OpenPulse
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="openpulse",
    version="1.0.0",
    author="OpenPulse Team",
    author_email="openpulse@example.com",
    description="Intelligent diagnostic and early warning platform for open source community vitality",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hwk603/openPulse",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "openpulse=src.api.main:main",
        ],
    },
)
