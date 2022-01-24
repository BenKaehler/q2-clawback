# ----------------------------------------------------------------------------
# Copyright (c) 2017-2022, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import tempfile
from warnings import filterwarnings

from qiime2 import Artifact
from qiime2.plugin.testing import TestPluginBase
from qiime2.plugins.feature_classifier.methods import \
    fit_classifier_naive_bayes
from qiime2.plugins.clawback.pipelines import assemble_weights_from_Qiita
from qiime2.plugins.clawback.methods import (
    sequence_variants_from_samples, generate_class_weights)
from qiime2.plugins.feature_classifier.methods import classify_sklearn
from biom import Table
from q2_types.feature_data import DNAIterator
from pandas import DataFrame, Series

import q2_clawback


class ClawbackTestPluginBase(TestPluginBase):
    package = 'q2_clawback.tests'

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(
            prefix='q2-clawback-test-temp-')

        filterwarnings('ignore', 'The TaxonomicClassifier ', UserWarning)
        self.reads = Artifact.import_data(
            'FeatureData[Sequence]',
            self.get_data_path('se-dna-sequences.fasta'))
        self.taxonomy = Artifact.import_data(
            'FeatureData[Taxonomy]', self.get_data_path('taxonomy.tsv'))
        classifier = fit_classifier_naive_bayes(self.reads, self.taxonomy)
        self.classifier = classifier.classifier

    def tearDown(self):
        self.temp_dir.cleanup()


class ClawbackTests(ClawbackTestPluginBase):
    def _check_weights(self, weights):
        seqs = self.reads.view(DNAIterator)
        tax = self.taxonomy.view(DataFrame)['Taxon']
        taxa = set(tax[s.metadata['id']]
                   for s in seqs if s.metadata['id'] in tax)
        self.assertEqual(taxa, set(weights.ids(axis='observation')))
        self.assertEqual(weights.shape, (len(taxa), 1))
        weights = weights.data('Weight')
        self.assertTrue((weights > 0.).all())
        self.assertTrue((weights < 1.).all())
        self.assertAlmostEqual(weights.sum(), 1.)

    def test_assemble_weights_from_Qiita(self):
        counts, caches = q2_clawback._clawback._fetch_Qiita_summaries()

        sample_type = 'Tears'
        self.assertTrue(hasattr(counts, sample_type))
        for context in caches.ContextName:
            if context.startswith('Deblur') and 'Illumina-16S-V4' in context:
                break
        else:
            self.assertTrue(False)

        weights = assemble_weights_from_Qiita(
            self.classifier, self.taxonomy, self.reads, [sample_type], context)
        weights = weights[0].view(Table)

        self._check_weights(weights)

    def test_allow_weight_outside_reference(self):
        samples = Artifact.import_data(
            'FeatureTable[Frequency]', self.get_data_path('tears.biom'))
        sample_reads = sequence_variants_from_samples(samples).sequences
        taxonomy = classify_sklearn(
            reads=sample_reads, classifier=self.classifier,
            confidence='disable', n_jobs=2, reads_per_batch=10)
        taxonomy = taxonomy.classification.view(Series)
        taxonomy['TACGGAGGGTGCAAGCGTTAATCGGAATTACTGGGCGTAAAGCGCGCGTAGGCGGCTAGG'
                 'TCAGTCAGATGTGAAAGCCCCGGGCTTAACCTGGGAATTG'] = 'Not a taxon'
        taxonomy = Artifact.import_data('FeatureData[Taxonomy]', taxonomy)
        with self.assertRaises(ValueError):
            weights = generate_class_weights(
                self.taxonomy, self.reads, samples, taxonomy)
        weights = generate_class_weights(
            self.taxonomy, self.reads, samples, taxonomy,
            allow_weight_outside_reference=True)
        weights = weights.class_weight.view(Table)

        self._check_weights(weights)
