# ----------------------------------------------------------------------------
# Copyright (c) 2017-2022, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import (Plugin, List, Str, Float, Bool, Int, Citations,
                           Range, Choices)
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
    citations=[citations['bokulich2018optimizing'],
               citations['kaehler2019species']],
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
    description='Display of counts of samples grouped by category and context',
    parameter_descriptions={
        'category': 'Metadata key over which to summarize sample counts'
    }
)

plugin.methods.register_function(
    function=q2_clawback.sequence_variants_from_samples,
    inputs={'samples': FeatureTable[Frequency]},
    parameters=None,
    outputs=[('sequences', FeatureData[Sequence])],
    name='Extract sequence variants from a feature table',
    description=('Extract sequence variants from a feature table, '
                 'if the feature table observations are labelled by sequence '
                 'variant'),
    input_descriptions={
        'samples': 'Feature table from which to extract sequence variants. '
                   'Features must be sequence variants.'
    },
    output_descriptions={
        'sequences': 'Features from the table as sequences'
    }
)

_generate_class_weights_input_descriptions = {
    'reference_taxonomy': 'Taxonomy that will be used when the weights from '
                          'this method are used to train a taxonomic '
                          'classifier',
    'reference_sequences': 'Sequences that will be used when the weights from '
                           'this method are used to train a taxonomic '
                           'classifier'
}

_generate_class_weights_parameter_descriptions = {
    'unobserved_weight': 'Resulting weights are a weighted sum of the weights '
                         'aggregated from samples and uniform weights across '
                         'all reference taxa (because zero weights are not '
                         'ok). unobserved_weight is the weight given to the '
                         'uniform weights in the sum',
    'normalise': 'Whether to normalise counts within samples prior to weight '
                 'aggregation',
    'allow_weight_outside_reference': 'Whether to allow sample weight for '
                                      'taxa that do not exist in the '
                                      'reference taxonomy. Such taxa are '
                                      'ignored if True'
}

_generate_class_weights_output_descriptions = {
    'class_weight': 'Taxonomic weights for use training taxonomic classifiers'
}


plugin.methods.register_function(
    function=q2_clawback.generate_class_weights,
    inputs={'reference_taxonomy': FeatureData[Taxonomy],
            'reference_sequences': FeatureData[Sequence],
            'samples': FeatureTable[Frequency],
            'taxonomy_classification': FeatureData[Taxonomy]},
    parameters={'unobserved_weight': Float,
                'normalise': Bool,
                'allow_weight_outside_reference': Bool},
    outputs=[('class_weight', FeatureTable[RelativeFrequency])],
    name='Generate class weights from a set of samples',
    description=('Generate class weights for use with a taxonomic classifier '
                 'from a set of existing observations'),
    input_descriptions={
        'samples': 'Samples from which to assemble weights',
        'taxonomy_classification': 'Taxonomy classification that maps the '
                                   'features in samples to taxa',
        **_generate_class_weights_input_descriptions
    },
    parameter_descriptions=_generate_class_weights_parameter_descriptions,
    output_descriptions=_generate_class_weights_output_descriptions
)

_fetch_Qiita_samples_parameter_descriptions = {
    'metadata_key': 'Fetch samples where this metadata key matches any '
                    'of the values in the metada value list',
    'metadata_value': 'Fetch samples where the metadata key matches this '
                      'value',
    'context': 'The redbiom context. Should be a context that contains '
               'SVs. Something like Deblur-Illumina-16S-V4-150nt-XXXXXX'
}


plugin.methods.register_function(
    function=q2_clawback.fetch_Qiita_samples,
    inputs={},
    parameters={'metadata_value': List[Str],
                'context': Str,
                'metadata_key': Str},
    outputs=[('samples', FeatureTable[Frequency])],
    name='Fetch feature counts for a collection of samples',
    description=('Fetch feature counts for a collection of samples, '
                 'preferably with SVs for OTU ids'),
    parameter_descriptions=_fetch_Qiita_samples_parameter_descriptions,
    output_descriptions={
        'samples': 'All the samples matching the query found in Qiita'
    }
)

plugin.pipelines.register_function(
    function=q2_clawback.assemble_weights_from_Qiita,
    inputs={'classifier': TaxonomicClassifier,
            'reference_taxonomy': FeatureData[Taxonomy],
            'reference_sequences': FeatureData[Sequence]},
    parameters={
        'metadata_value': List[Str],
        'context': Str,
        'unobserved_weight': Float,
        'normalise': Bool,
        'metadata_key': Str,
        'n_jobs': Int,
        'reads_per_batch': Int % Range(1, None) | Str % Choices(['auto']),
        'allow_weight_outside_reference': Bool},
    outputs=[('class_weight', FeatureTable[RelativeFrequency])],
    name='Assemble weights from Qiita for use with q2-feature-classifier',
    description=('Download SV results from Qiita, classify the SVs, use the '
                 'result to collate class weights'),
    input_descriptions={
        'classifier': 'Taxonomic classifier to be used to classify SVs prior '
                      'to taxonomic weight assembly',
        **_generate_class_weights_input_descriptions
    },
    parameter_descriptions={
        'n_jobs': 'The maximum number of concurrently worker processes. If -1 '
                  'all CPUs are used. If 1 is given, no parallel computing '
                  'code is used at all, which is useful for debugging. For '
                  'n_jobs below -1, (n_cpus + 1 + n_jobs) are used. Thus for '
                  'n_jobs = -2, all CPUs but one are used.',
        'reads_per_batch': 'Number of reads to process in each batch. If 0, '
                           'this parameter is autoscaled to '
                           'min( number of query sequences / n_jobs, 20000).',
        **_fetch_Qiita_samples_parameter_descriptions,
        **_generate_class_weights_parameter_descriptions
    },
    output_descriptions=_generate_class_weights_output_descriptions
)
