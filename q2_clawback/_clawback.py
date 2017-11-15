# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
from collections import Counter

import pkg_resources
import biom
import q2templates
import redbiom.fetch
import redbiom.summarize
import redbiom.search
from pandas import Series
from numpy import array

TEMPLATES = pkg_resources.resource_filename('q2_clawback', 'assets')


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


def create_class_weights(
        taxonomy: Series, table: biom.Table, background_weight: float):
    ids = table.ids(axis='observation')
    normed_table = table.norm(inplace=False)
    nonzero_weights = normed_table.sum(axis='observation') / table.length()
    nonzero_weights = dict(zip(ids, nonzero_weights))

    weights = Counter()
    for seq_id, taxon in taxonomy.items():
        if seq_id in nonzero_weights:
            weights[taxon] += nonzero_weights[seq_id]
        else:
            weights[taxon] += 0

    taxa, weights = zip(*weights.items())
    weights = array(weights)
    weights *= 1. - background_weight
    zero_weights = weights == 0
    weights[zero_weights] = background_weight / sum(zero_weights)

    return biom.Table(weights[None].T, taxa, sample_ids=['Weight'])


def summarize_QIITA_features(
        reference_taxonomy: Series, sample_type: list, context: str,
        background_weight: float=1e-6) -> biom.Table:
    table = fetch_QIITA_features(sample_type, context)
    weights = create_class_weights(
        reference_taxonomy, table, background_weight)
    return weights
