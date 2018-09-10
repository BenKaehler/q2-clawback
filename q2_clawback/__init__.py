# ----------------------------------------------------------------------------
# Copyright (c) 2017-2018, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._version import get_versions
from ._clawback import (summarize_Qiita_metadata_category_and_contexts,
                        fetch_Qiita_samples,
                        sequence_variants_from_samples,
                        generate_class_weights,
                        assemble_weights_from_Qiita)
from ._knn import precalculate_nearest_neighbors, kNN_LOOCV_F_measures
from ._format import (PrecalculatedNearestNeighborsFormat,
                      PrecalculatedNearestNeighborsDirectoryFormat)
from ._type import PrecalculatedNearestNeighbors

__all__ = ['summarize_Qiita_metadata_category_and_contexts',
           'sequence_variants_from_samples',
           'fetch_Qiita_samples',
           'generate_class_weights',
           'assemble_weights_from_Qiita',
           'precalculate_nearest_neighbors',
           'kNN_LOOCV_F_measures',
           'PrecalculatedNearestNeighborsFormat',
           'PrecalculatedNearestNeighborsDirectoryFormat',
           'PrecalculatedNearestNeighbors']

__version__ = get_versions()['version']
del get_versions
