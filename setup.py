#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='osu_diffcalc_gui',
    version='0.1.0',
    description='GUI for testing osu difficulty calculation',
    author='Joseph Ireland',
    author_email='joseph.ireland@outlook.com',
    packages=find_packages(),
    package_data={"osu_diffcalc_gui":["map.osu.jinja"]},
    include_package_data=True,
    license='GPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Games/Entertainment',
    ],
    url='https://github.com/joseph-ireland/osu_diffcalc_gui',
    install_requires=[
        'PySide2',
        'jinja2',
    ],
)