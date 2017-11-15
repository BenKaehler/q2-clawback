# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import Plugin, List, Str, Float
from q2_types.feature_table import FeatureTable, RelativeFrequency
from q2_types.feature_data import FeatureData, Taxonomy

import q2_clawback

plugin = Plugin(
    name='clawback',
    version=q2_clawback.__version__,
    website='https://github.com/BenKaehler/q2-clawback',
    package='q2_clawback',
    citation_text=("Something Awesome. Kaehler B, Bokulich, N. "
                   "J. Awesome. 2018"),
    description=('This QIIME 2 plugin provides support for generating '
                 'generating class weights for use with the '
                 'feature-classifier'),
    short_description='CLAss Weight Assembler plugin.'
)

plugin.visualizers.register_function(
    function=q2_clawback.summarize_QIITA_sample_types_and_contexts,
    inputs={},
    parameters={},
    name='Fetch QIITA sample types and contexts',
    description='Display of counts of samples by sample type and context'
)

plugin.methods.register_function(
    function=q2_clawback.summarize_QIITA_features,
    inputs={'reference_taxonomy': FeatureData[Taxonomy]},
    parameters={'sample_type': List[Str],
                'context': Str,
                'background_weight': Float},
    outputs=[('class_weight', FeatureTable[RelativeFrequency])],
    name='Assemble the taxonomy weights from a set of samples',
    description='Assemble the taxonomy weights for a set of QIITA samples'
)
