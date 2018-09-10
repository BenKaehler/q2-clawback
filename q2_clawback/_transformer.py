# ----------------------------------------------------------------------------
# Copyright (c) 2017-2018, Ben Kaehler.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json

from .plugin_setup import plugin
from ._format import PrecalculatedNearestNeighborsFormat, \
    _validate_precalculated_nearest_neighbors


@plugin.register_transformer
def _1(data: dict) -> PrecalculatedNearestNeighborsFormat:
    _validate_precalculated_nearest_neighbors(data)
    ff = PrecalculatedNearestNeighborsFormat()
    with ff.open() as fh:
        json.dump(data, fh)
    return ff


@plugin.register_transformer
def _2(ff: PrecalculatedNearestNeighborsFormat) -> dict:
    with ff.open() as fh:
        return json.load(fh)
