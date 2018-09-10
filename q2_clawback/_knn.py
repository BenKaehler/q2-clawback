# ----------------------------------------------------------------------------
# Copyright (c) 2017-2018, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import json
from collections import Counter

import pkg_resources
from imblearn.under_sampling import ClusterCentroids
from sklearn.base import TransformerMixin
from sklearn.neighbors.base import KNeighborsMixin
from pandas import Series, DataFrame
from sklearn.metrics import f1_score
import q2templates
from q2_types.feature_data import DNAIterator
from q2_feature_classifier.classifier import pipeline_from_spec
from q2_feature_classifier._skl import _extract_reads

TEMPLATES = pkg_resources.resource_filename('q2_clawback', 'assets')

_default_feature_extractor = (
    '[["ext", {'
    '"analyzer": "char_wb", '
    '"__type__": "feature_extraction.text.HashingVectorizer", '
    '"n_features": 8192, '
    '"strip_accents": null, '
    '"ngram_range": [7, 7], '
    '"alternate_sign": false'
    '}]]'
)

_default_knn_classifier = \
    '[["cls", {"__type__": "neighbors.NearestNeighbors", "n_neighbors": 11}]]'


def precalculate_nearest_neighbors(
        reference_taxonomy: Series, reference_sequences: DNAIterator,
        max_centroids_per_class: int=10,
        feature_extractor_specification: str=_default_feature_extractor,
        knn_classifier_specification: str=_default_knn_classifier,
        n_jobs: int=1, random_state: int=42) -> dict:
    spec = json.loads(feature_extractor_specification)
    feat_ext = pipeline_from_spec(spec)
    if not isinstance(feat_ext.steps[-1][-1], TransformerMixin):
        raise ValueError('feature_extractor_specification must specify a '
                         'transformer')
    spec = json.loads(knn_classifier_specification)
    nn = pipeline_from_spec(spec)
    if not isinstance(nn.steps[-1][-1], KNeighborsMixin):
        raise ValueError('knn_classifier_specification must specifiy a '
                         'KNeighbors classifier')

    seq_ids, X = _extract_reads(reference_sequences)
    data = [(reference_taxonomy[s], x)
            for s, x in zip(seq_ids, X) if s in reference_taxonomy]
    y, X = list(zip(*data))
    X = feat_ext.transform(X)

    if max_centroids_per_class > 0:
        class_counts = Counter(y)
        undersample_classes = {t: max_centroids_per_class
                               for t, c in class_counts.items()
                               if c > max_centroids_per_class}
        cc = ClusterCentroids(random_state=random_state, n_jobs=n_jobs,
                              ratio=undersample_classes, voting='hard')
        X_resampled, y_resampled = cc.fit_sample(X, y)
    else:
        X_resampled, y_resampled = X, y

    if 'n_jobs' in nn.steps[-1][-1].get_params():
        nn.steps[-1][-1].set_params(n_jobs=n_jobs)
    nn.fit(X_resampled)
    nn = nn.steps[-1][-1]
    if n_jobs != 1 and hasattr(X_resampled, 'todense'):
        indices = nn.kneighbors(X_resampled.todense(), return_distance=False)
    else:
        indices = nn.kneighbors(X_resampled, return_distance=False)
    return {'neighbors': indices.tolist(), 'taxonomies': y_resampled.tolist()}


def _loocv(y, indices, weights, uniform_prior=False):
    yfreq = Counter(y)
    if uniform_prior:
        sample_weights = [1./len(yfreq)/yfreq[t] for t in y]
    else:
        if yfreq.keys() != weights.keys():
            raise ValueError('Nearest neighbors and weights were calculated '
                             'using different reference data sets')
        sample_weights = [weights[t]/yfreq[t] for t in y]
    pred = []
    for row in indices:
        vote = Counter()
        for ix in row[1:]:
            vote[y[ix]] += sample_weights[ix]
        pred.append(vote.most_common()[0][0])
    if uniform_prior:
        sample_weights = [weights[t]/yfreq[t] for t in y]
    return f1_score(y, pred, average='weighted', sample_weight=sample_weights)


def kNN_LOOCV_F_measures(output_dir: str,
                         nearest_neighbors: dict, class_weight: DataFrame):
    y = nearest_neighbors['taxonomies']
    indices = nearest_neighbors['neighbors']
    weights = class_weight.T['Weight'].to_dict()
    uniform = _loocv(y, indices, weights, True)
    bespoke = _loocv(y, indices, weights)
    index = os.path.join(TEMPLATES, 'index.html')
    f_measures = DataFrame({'F-measure': [bespoke, uniform, bespoke-uniform]},
                           index=['Weighted', 'Uniform', 'Difference'])
    f_measures = q2templates.df_to_html(f_measures)
    q2templates.render(index, output_dir, context={
        'title': 'Indicators of Taxonomic Weight Importance',
        'f_measures': f_measures,
    })
