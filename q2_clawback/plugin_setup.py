# ----------------------------------------------------------------------------
# Copyright (c) 2017-2018, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from qiime2.plugin import Plugin, List, Str, Float, Bool, Citations, Int
from q2_types.feature_table import FeatureTable, RelativeFrequency, Frequency
from q2_types.feature_data import FeatureData, Taxonomy, Sequence
from q2_feature_classifier._taxonomic_classifier import TaxonomicClassifier

import q2_clawback

citations = Citations.load('citations.bib', package='q2_clawback')
plugin = Plugin(
    name='clawback',
    version=q2_clawback.__version__,
    website='https://github.com/BenKaehler/q2-clawback',
    package='q2_clawback',
    citations=[citations['bokulich2018optimizing']],
    description=('This QIIME 2 plugin provides support for generating '
                 'generating class weights for use with the '
                 'feature-classifier'),
    short_description='CLAss Weight Assembler plugin.'
)

plugin.visualizers.register_function(
    function=q2_clawback.summarize_Qiita_metadata_category_and_contexts,
    inputs={},
    parameters={'category': Str},
    name='Fetch Qiita sample types and contexts',
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
    function=q2_clawback.fetch_Qiita_samples,
    inputs={},
    parameters={'metadata_value': List[Str],
                'context': Str,
                'metadata_key': Str},
    outputs=[('samples', FeatureTable[Frequency])],
    name='Fetch feature counts for a collection of samples',
    description=('Fetch feature counts for a collection of samples, '
                 'preferebly with SVs for OTU ids')
)

plugin.pipelines.register_function(
    function=q2_clawback.assemble_weights_from_Qiita,
    inputs={'classifier': TaxonomicClassifier,
            'reference_taxonomy': FeatureData[Taxonomy],
            'reference_sequences': FeatureData[Sequence]},
    parameters={'metadata_value': List[Str],
                'context': Str,
                'unobserved_weight': Float,
                'normalise': Bool,
                'metadata_key': Str},
    outputs=[('class_weight', FeatureTable[RelativeFrequency])],
    name='Assemble weights from Qiita for use with q2-feature-classifier',
    description=('Download SV results from Qiita, classify the SVs, use the '
                 'result to collate class weights')
)

plugin.methods.register_function(
    function=q2_clawback.precalculate_nearest_neighbors,
    inputs={'reference_taxonomy': FeatureData[Taxonomy],
            'reference_sequences': FeatureData[Sequence]},
    parameters={'max_centroids_per_class': Int,
                'feature_extractor_specification': Str,
                'knn_classifier_specification': Str,
                'n_jobs': Int,
                'random_state': Int},
    outputs=[('nearest_neighbors', q2_clawback.PrecalculatedNearestNeighbors)],
    name='Calculate nearest neighbors for estimating class weight importance',
    description=('Fit a kNN classifier to the optionally undersampled '
                 'reference data and cache the neighbors')
)

plugin.visualizers.register_function(
    function=q2_clawback.kNN_LOOCV_F_measures,
    inputs={'nearest_neighbors': q2_clawback.PrecalculatedNearestNeighbors,
            'class_weight': FeatureTable[RelativeFrequency]},
    parameters={},
    name='Estimate importance of class weights',
    description=('Calculated k Nearest Neighbors Leave-One-Out Cross '
                 'Validated F-measures for weighted and uniform assumptions')
)

plugin.register_semantic_types(q2_clawback.PrecalculatedNearestNeighbors)
plugin.register_formats(
    q2_clawback.PrecalculatedNearestNeighborsFormat,
    q2_clawback.PrecalculatedNearestNeighborsDirectoryFormat
)
plugin.register_semantic_type_to_format(
    q2_clawback.PrecalculatedNearestNeighbors,
    artifact_format=q2_clawback.PrecalculatedNearestNeighborsDirectoryFormat
)
importlib.import_module('q2_clawback._transformer')
