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


def sequence_variants_from_feature_table(table: biom.Table) -> DNAIterator:
    seqs = (DNA(s, metadata={'id': s}) for s in table.ids(axis='observation'))
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


def fetch_QIITA_features(sample_type: list, context: str) -> biom.Table:
    query = "where sample_type == '"
    query += "' or sample_type == '".join(sample_type)
    query += "'"
    sample_ids = redbiom.search.metadata_full(query, False)
    table, ambig = redbiom.fetch.data_from_samples(context, sample_ids)
    return table


def generate_class_weights(
        reference_taxonomy: Series, reference_sequences: DNAIterator,
        table: biom.Table, taxonomy_classification: DataFrame=None,
        unobserved_weight: float=1e-6, normalise: bool=False) -> biom.Table:
    weights = {reference_taxonomy[seq.metadata['id']]: 0.
               for seq in reference_sequences}
    if normalise:
        table.norm()

    if taxonomy_classification is not None:
        tax_map = taxonomy_classification['Taxon']
        try:
            taxa = [tax_map[s] for s in table.ids(axis='observation')]
        except KeyError as s:
            raise ValueError(str(s) + ' not in taxonomy_classification')
        if not set(taxa).issubset(weights):
            raise ValueError(
                'taxonomy_classification does not match reference_taxonomy')
    else:
        try:
            taxa = [reference_taxonomy[s]
                    for s in table.ids(axis='observation')]
        except KeyError as s:
            raise ValueError(str(s) + ' not in reference_taxonomy')

    for taxon, count in zip(taxa, table.sum('observation')):
        weights[taxon] += count
    taxa, weights = zip(*weights.items())
    weights = array(weights)
    weights /= weights.sum()
    weights = (1. - unobserved_weight)*weights + unobserved_weight/len(weights)
    weights /= weights.sum()

    return biom.Table(weights[None].T, taxa, sample_ids=['Weight'])


def summarize_QIITA_features(
        reference_taxonomy: Series, sample_type: list, context: str,
        unobserved_weight: float=1e-6) -> biom.Table:
    table = fetch_QIITA_features(sample_type, context)
    weights = generate_class_weights(
        reference_taxonomy, table, unobserved_weight)
    return weights
