# ----------------------------------------------------------------------------
# Copyright (c) 2017-2018, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json

import qiime2.plugin.model as model
from qiime2.plugin import ValidationError


def _validate_precalculated_nearest_neighbors(flat_nn):
    if not isinstance(flat_nn, dict):
        raise ValidationError("Expected JSON-encoded dict")
    if "neighbors" not in flat_nn or "taxonomies" not in flat_nn:
        raise ValidationError('Expected dict to have keys '
                              '"neighbors" and "taxonomies"')
    if not all(isinstance(v, list) for v in flat_nn.values()):
        raise ValidationError("Expected dict of lists")
    if len(flat_nn["neighbors"]) != len(flat_nn["taxonomies"]):
        raise ValidationError('Expected neighbors and taxonomies '
                              'to have equal lengths')


class PrecalculatedNearestNeighborsFormat(model.TextFileFormat):
    def validate(self, level):
        with self.open() as fh:
            try:
                _validate_precalculated_nearest_neighbors(json.load(fh))
            except json.JSONDecodeError as e:
                raise ValidationError(e)


PrecalculatedNearestNeighborsDirectoryFormat = \
    model.SingleFileDirectoryFormat(
        'PrecalculatedNearestNeighborsDirectoryFormat',
        'nearest_neighbors.json', PrecalculatedNearestNeighborsFormat)
