# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import Plugin, List, Str, Float, Bool
from q2_types.feature_table import FeatureTable, RelativeFrequency, Frequency
from q2_types.feature_data import FeatureData, Taxonomy, Sequence
from q2_feature_classifier._taxonomic_classifier import TaxonomicClassifier

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
    function=q2_clawback.sequence_variants_from_samples,
    inputs={'samples': FeatureTable[Frequency]},
    parameters=None,
    outputs=[('sequences', FeatureData[Sequence])],
    name='Extract sequence variants from a feature table',
    description=('Extract sequence variants from a feature table, '
                 'if the feature table observations are labelled by sequence '
                 'variant')
)

plugin.methods.register_function(
    function=q2_clawback.generate_class_weights,
    inputs={'reference_taxonomy': FeatureData[Taxonomy],
            'reference_sequences': FeatureData[Sequence],
            'samples': FeatureTable[Frequency],
            'taxonomy_classification': FeatureData[Taxonomy]},
    parameters={'unobserved_weight': Float, 'normalise': Bool},
    outputs=[('class_weight', FeatureTable[RelativeFrequency])],
    name='Generate class weights from a set of samples',
    description=('Generate class weights for use with a taxonomic classifier '
                 'from a set of existing observations')
)

plugin.methods.register_function(
    function=q2_clawback.fetch_QIITA_samples,
    inputs={},
    parameters={'sample_type': List[Str],
                'context': Str},
    outputs=[('samples', FeatureTable[Frequency])],
    name='Fetch feature counts for a collection of samples',
    description=('Fetch feature counts for a collection of samples, '
                 'preferebly with SVs for OTU ids')
)

plugin.pipelines.register_function(
    function=q2_clawback.assemble_weights_from_QIITA_sample_types,
    inputs={'classifier': TaxonomicClassifier,
            'reference_taxonomy': FeatureData[Taxonomy],
            'reference_sequences': FeatureData[Sequence]},
    parameters={'sample_type': List[Str],
                'context': Str,
                'unobserved_weight': Float,
                'normalise': Bool},
    outputs=[('samples', FeatureTable[RelativeFrequency])],
    name='Assemble weights from QIITA for use with q2-feature-classifier',
    description=('Download SV results from QIITA, classify the SVs, use the '
                 'result to collate class weights')
)
