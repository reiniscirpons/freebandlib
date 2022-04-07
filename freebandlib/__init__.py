# -*- coding: utf-8 -*-

# Copyright (c) 2022, Reinis Cirpons + J. D. Mitchell
#
# Distributed under the terms of the GPL license version 3.
#
# The full license is in the file LICENSE, distributed with this software.

"""
This package provides the user-facing functionality of freebandlib
"""

from .digraph import (
    digraph_is_reachable,
    digraph_reverse,
    digraph_topological_order,
)

# from .minword import min_word

from .equality import equivalent_words, equivalent_transducers

from .multiply import multiply

from .transducer import (
    Transducer,
    transducer_connected_states,
    transducer_cont,
    transducer_minimize,
    transducer_isomorphism,
    transducer_topological_order,
    transducer_induced_subtransducer,
)

from .words import cont, pref_ltof, suff_ftol, word_function
