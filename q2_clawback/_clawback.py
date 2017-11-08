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

TEMPLATES = pkg_resources.resource_filename('q2_clawback', 'assets')


def fetch_QIITA_community_types(output_dir: str=None):
    import redbiom.fetch
    category = 'sample_type'
    descending = True
    md = redbiom.fetch.category_sample_values(category)
    counts = md.value_counts(ascending=not descending)
    result = q2templates.df_to_html(counts.to_frame())
    title = 'wtf'
    index = os.path.join(TEMPLATES, 'index.html')
    q2templates.render(index, output_dir, context={
        'title': title,
        'result': result})


def fetch_QIITA_samples_for_type():
    pass


def assemble_taxonomy_weights() -> biom.Table:
    pass
