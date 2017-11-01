# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import Plugin

import q2_clawback

plugin = Plugin(
    name='clawback',
    version=q2_clawback.__version__,
    website='https://github.com/BenKaehler/q2-clawback',
    package='q2_clawback',
    citation_text=("Something Awesome. Kaehler B, Bokulich, N. "
                   "J. Awesome. 2018"),
    description=('This QIIME 2 plugin provides support for generating '
                 'generating class weights for use with the ',
                 'feature-classifier'),
    short_description='CLAss Weight Assembler plugin.'
)

plugin.methods.register_function(
    function=q2_clawback.fetch_QIITA_community_types,
    inputs={},
    parameters={},
    outputs=[],
    input_descriptions={},
    parameter_descriptions={},
    output_descriptions={},
    name='Fetch QIITA community types',
    description=("Fetch community types from QIITA")
)

plugin.methods.register_function(
    function=q2_clawback.fetch_QIITA_samples_for_type,
    inputs={},
    parameters={},
    outputs=[],
    input_descriptions={},
    parameter_descriptions={},
    output_descriptions={},
    name='Fetch QIITA sample labels',
    description=("Fetch samples from QIITA for a given community type")
)

plugin.methods.register_function(
    function=q2_clawback.assemble_taxonomy_weights,
    inputs={},
    parameters={},
    outputs=[],
    input_descriptions={},
    parameter_descriptions={},
    output_descriptions={},
    name='Assemble the taxonomy weights from a set of samples',
    description=("Assemble the taxonomy weights for a set of QIITA samples")
)
