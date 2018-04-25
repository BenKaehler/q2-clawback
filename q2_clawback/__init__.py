# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._version import get_versions
from ._clawback import (summarize_QIITA_sample_types_and_contexts,
                        fetch_QIITA_features,
                        summarize_QIITA_features,
                        sequence_variants_from_feature_table,
                        generate_class_weights)

__all__ = ['summarize_QIITA_sample_types_and_contexts',
           'summarize_QIITA_features',
           'sequence_variants_from_feature_table',
           'fetch_QIITA_features',
           'generate_class_weights']

__version__ = get_versions()['version']
del get_versions
