# ----------------------------------------------------------------------------
# Copyright (c) 2017-2022, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import setup, find_packages

import versioneer


setup(
    name="q2-clawback",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    author="Ben Kaehler",
    author_email="kaehler@gmail.com",
    description="Create and work with class weights in QIIME 2.",
    license="BSD-3-Clause",
    url="https://qiime2.org",
    entry_points={
        'qiime2.plugins': ['q2-clawback=q2_clawback.plugin_setup:plugin']
    },
    package_data={'q2_clawback': ['assets/index.html', 'citations.bib'],
                  'q2_clawback.tests': ['data/*']},
    zip_safe=False,
)
