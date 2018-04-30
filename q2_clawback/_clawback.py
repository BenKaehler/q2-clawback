# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os

import pkg_resources
import biom
import q2templates
import redbiom.fetch
import redbiom.summarize
import redbiom.search
from pandas import Series, DataFrame
from numpy import array
from skbio import DNA
from q2_types.feature_data import DNAIterator

TEMPLATES = pkg_resources.resource_filename('q2_clawback', 'assets')


def sequence_variants_from_samples(samples: biom.Table) -> DNAIterator:
    seqs = (DNA(s, metadata={'id': s})
            for s in samples.ids(axis='observation'))
    return DNAIterator(seqs)


def summarize_QIITA_sample_types_and_contexts(output_dir: str=None):
    md = redbiom.fetch.category_sample_values('sample_type')
    counts = md.value_counts(ascending=False)
    sample_types = q2templates.df_to_html(
        counts.to_frame(), bold_rows=False, header=False)
    caches = redbiom.summarize.contexts()[['ContextName', 'SamplesWithData']]
    caches = caches.sort_values(by='SamplesWithData', ascending=False)
    contexts = q2templates.df_to_html(caches, index=False)
    title = 'Available in QIITA'
    index = os.path.join(TEMPLATES, 'index.html')
    q2templates.render(index, output_dir, context={
        'title': title,
        'sample_types': sample_types,
        'contexts': contexts})


def fetch_QIITA_samples(sample_type: list, context: str) -> biom.Table:
    query = "where sample_type == '"
    query += "' or sample_type == '".join(sample_type)
    query += "'"
    sample_ids = redbiom.search.metadata_full(query, False)
    samples, ambig = redbiom.fetch.data_from_samples(context, sample_ids)
    return samples


def generate_class_weights(
        reference_taxonomy: Series, reference_sequences: DNAIterator,
        samples: biom.Table, taxonomy_classification: DataFrame,
        unobserved_weight: float=1e-6, normalise: bool=False) -> biom.Table:
    weights = {reference_taxonomy[seq.metadata['id']]: 0.
               for seq in reference_sequences}
    if normalise:
        samples.norm()

    tax_map = taxonomy_classification['Taxon']
    try:
        taxa = [tax_map[s] for s in samples.ids(axis='observation')]
    except KeyError as s:
        raise ValueError(str(s) + ' not in taxonomy_classification')
    if not set(taxa).issubset(weights):
        raise ValueError(
            'taxonomy_classification does not match reference_taxonomy')

    for taxon, count in zip(taxa, samples.sum('observation')):
        weights[taxon] += count
    taxa, weights = zip(*weights.items())
    weights = array(weights)
    weights /= weights.sum()
    weights = (1. - unobserved_weight)*weights + unobserved_weight/len(weights)
    weights /= weights.sum()

    return biom.Table(weights[None].T, taxa, sample_ids=['Weight'])


def assemble_weights_from_QIITA_sample_types(
        ctx, classifier, reference_taxonomy, reference_sequences, sample_type,
        context, unobserved_weight=1e-6, normalise=False):
    samples, = ctx.get_action('clawback', 'fetch_QIITA_samples')(
        sample_type=sample_type, context=context)

    reads, = ctx.get_action('clawback', 'sequence_variants_from_samples')(
        samples=samples)

    classification, = ctx.get_action('feature-classifier', 'classify_sklearn')(
        reads=reads, classifier=classifier, confidence=-1)

    return tuple(ctx.get_action('clawback', 'generate_class_weights')(
        reference_taxonomy=reference_taxonomy,
        reference_sequences=reference_sequences,
        samples=samples, taxonomy_classification=classification,
        unobserved_weight=unobserved_weight, normalise=normalise))
