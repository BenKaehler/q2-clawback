# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._version import get_versions
from ._clawback import (summarize_QIITA_metadata_category_and_contexts,
                        fetch_QIITA_samples,
                        sequence_variants_from_samples,
                        generate_class_weights,
                        assemble_weights_from_QIITA)

__all__ = ['summarize_QIITA_metadata_category_and_contexts',
           'sequence_variants_from_samples',
           'fetch_QIITA_samples',
           'generate_class_weights',
           'assemble_weights_from_QIITA']

__version__ = get_versions()['version']
del get_versions
