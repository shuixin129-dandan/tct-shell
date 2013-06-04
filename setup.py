#!/usr/bin/python

from glob import glob

from setuptools import setup, find_packages

setup(
    name = "tct-shell",
    description = "Console tool for Tizen Compliance Test",
    author = "Cathy Shen",
    author_email = "cathy.shen@intel.com",
    version = "1.0.0",
    include_package_data = True,
    data_files = [('/opt/tct/shell/plan', glob('plan/*')),
	          ('/opt/tct/shell/', ['CONFIG', 'LICENSE', 'VERSION']),
                  ('/opt/tct/shell/style', glob('style/*'))],
    scripts = ['tct-shell', 'tct-plan-generator'],
    packages = find_packages(),
)
