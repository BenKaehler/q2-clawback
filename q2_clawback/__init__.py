# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._version import get_versions
from ._clawback import (fetch_QIITA_community_types,
                        fetch_QIITA_samples_for_type,
                        assemble_taxonomy_weights)

__all__ = ['fetch_QIITA_community_types', 'fetch_QIITA_samples_for_type',
           'assemble_taxonomy_weights']

__version__ = get_versions()['version']
del get_versions
