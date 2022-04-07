"""Transducer utility functions.

In this section we implement datastructures and algorithms for representing and
working with transducers.

These datastructures are tailored to our specific use-case and therefore are
not intended to cover the full generality of transducer theory.
Rather we have choosen them to allow us to implement the algorithms described
in the companion paper to this library (TODO:reference) in a fairly efficient
and understandable manner while retaining the time and space complexities from
the paper.

In particular, throughout this implementation, we assume that our input
alphabet is :math:`{0, 1}` and our output alphabets are always finite sets of
the form :math:`{0, 1, ..., n}` for some :math`n`.

TODO: Finish
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Set

from freebandlib.digraph import (
    DigraphAdjacencyList,
    digraph_is_reachable,
    digraph_reverse,
    digraph_topological_order,
)
from freebandlib.words import (
    InputLetter,
    InputWord,
    OutputLetter,
    OutputWord,
    compute_left,
    compute_right,
    cont,
    pref_ltof,
    suff_ftol,
)

# Each transducer state is assigned an identifier. These are required to be
# non-negative integers.
StateId = int


class Transducer:
    """A datastructure representing a transducer.

    Parameters
    ----------
    initial: Optional[StateId]
        The the position of the initial state in the `states` list.
        Can be `None` to support empty transducer.
    next_state: List[List[Optional[StateId]]]
        The state transition function
    next_letter: List[List[Optional[Letter]]]
        The letter transition function
    terminal: List[bool]
        A list indicating if the `i`-th state is terminal or not.

    Other Parameters
    ----------------
    label: List[str], default=None
        A list of node labels. These are optional and only serve a purpose for
        debugging or visualising.

    Notes
    -----
    We assume that our transducers are synchronous, deterministic and acyclic,
    so that no epsilon transitions are permitted, each input letter leads to
    exactly one state, and outputs exactly one output letter, and furthermore
    no directed cycle can occur which implies the function they realize have a
    finite domain but is a stronger condition.

    Since the input alphabet is always :math:`{0, 1}`, we opt to store our
    state transition and letter transition functions as lists, where the
    :math:`i`-th entry corresponds to the transition upon reading :math:`i` (if
    this transition is defined and `None` otherwise).
    """

    def __init__(
        self,
        initial: Optional[StateId],
        next_state: List[List[Optional[StateId]]],
        next_letter: List[List[Optional[StateId]]],
        terminal: List[bool],
        label: List[str] = None,
    ):
        self.initial = initial
        self.next_letter = next_letter
        self.next_state = next_state
        self.terminal = terminal
        self.label = label
        self.validate()  # TODO(RC) not sure if you want this here!

    @property
    def nr_states(self) -> int:
        return len(self.next_letter)

    def copy(self) -> Transducer:
        return Transducer(
            self.initial,
            self.next_state[::],
            self.next_letter[::],
            self.terminal[::],
            self.label[::] if self.label is not None else None,
        )

    def validate(self):
        if not (self.initial is None or isinstance(self.initial, StateId)):
            raise RuntimeError("self.initial must be None or a StateId")
        if self.initial is not None and (
            self.initial >= self.nr_states or self.initial < 0
        ):
            raise RuntimeError(
                f"self.initial must be in the range [0, {self.nr_states}"
            )
        if not (
            isinstance(self.next_state, List)
            and all(
                x is None or isinstance(x, StateId) for x in self.next_state
            )
        ):
            raise RuntimeError(
                "self.next_state must be a list of optional StateId objects"
            )
        if not (
            isinstance(self.next_letter, List)
            and all(
                x is None or isinstance(x, OutputLetter)
                for x in self.next_letter
            )
        ):
            raise RuntimeError(
                "self.next_letter must be a list of optional OutputLetter objects"
            )
        if not (
            len(self.next_state) == len(self.next_letter)
            and all(
                (x is None and y is None)
                or (isinstance(x, StateId) and isinstance(y, OutputLetter))
                for x, y in zip(self.next_state, self.next_letter)
            )
        ):
            raise RuntimeError(
                "self.next_state and self.next_letter must have the same length and be defined on the same inputs"
            )
        if not (
            isinstance(self.terminal, List)
            and all(isinstance(x, bool) for x in self.terminal)
        ):
            raise RuntimeError("self.terminal must be a list of bools")
        if not (
            self.label is None
            or (
                isinstance(self.label, list)
                and all(isinstance(x, str) for x in self.label)
            )
        ):
            raise RuntimeError(
                f"self.label must be None or a List[str] not {type(self.label)}"
            )
        if self.nr_states != len(self.terminal):
            raise RuntimeError("self.terminal must be defined for all states")
        if self.label is not None and self.nr_states != len(self.label):
            raise RuntimeError(
                "if defined, self.label must be defined on all states"
            )

    def __repr__(self):
        """Generate a textual representation of the transducer."""
        return repr(
            (self.initial, self.next_state, self.next_letter, self.terminal)
        )

    def add_state(
        self,
        next_state: List[Optional[StateId]],
        next_letter: List[Optional[OutputLetter]],
        is_terminal: bool,
    ) -> StateId:
        """Add a state to the transducer.

        This method modifies the transducer to have a new state with properties
        specified by the arguments.

        Parameters
        ----------
        next_state_id: NextStateId
            A state id transition function.
        next_letter: NextLetter
            A letter transition function.
        is_terminal: bool
            A boolean indicating if the state is terminal.

        Returns
        -------
        StateId
            The state that was added to the transducer.
        """
        self.next_state.append(next_state)
        self.next_letter.append(next_letter)
        self.terminal.append(is_terminal)
        return self.nr_states - 1

    def traverse(self, word: InputWord) -> Optional[OutputWord]:
        """Traverse an input word through the trasducer and return its output.

        Parameters
        ----------
        word: InputWord
            An input word.

        Returns
        -------
        Optional[OutputWord]
            The output word corresponding to the input, if a terminal state is
            reached while traversing the input word and None otherwise.

        Notes
        -----
        TODO: Just add a reference here?
        """
        if self.initial is None:
            return None

        state: Optional[StateId] = self.initial
        result: OutputWord = []
        result_letter: Optional[OutputLetter]
        for letter in word:
            assert state is not None
            result_letter = self.next_letter[state][letter]
            if result_letter is None:
                return None
            result.append(result_letter)
            state = self.next_state[state][letter]

        if state is None or not self.terminal[state]:
            return None

        return result

    def underlying_digraph(self) -> DigraphAdjacencyList:
        """Return the underlying graph of the transducer.

        Returns
        -------
        DigraphAdjacencyList
            The adjacency list of the underlying graph of the transducer.

        Notes
        -----
        Every transducer has an underlying digraph structure whose vertices are
        given by states and there is an edge from one vertex to another if
        there is a state transition between the corresponding states.
        """
        state: StateId
        child: Optional[StateId]

        result: DigraphAdjacencyList = [[] for _ in range(self.nr_states)]
        for state in range(self.nr_states):
            for child in self.next_state[state]:
                if child is not None and child not in result[state]:
                    result[state].append(child)

        return result


def transducer_connected_states(transducer: Transducer) -> List[StateId]:
    """Return all the connected state ids of a given transducer.

    Parameters
    ----------
    transducer: Transducer

    Returns
    -------
    List[StateId]
        The connected states given by their state ids.

    See Also
    --------
    transducer_trim: A function that removes all disconnected states.

    Notes
    -----
    A transducer state is _accessible_ if it there is a path leading to it from
    the initial state. It is _coaccessible_ if there is a path from it to a
    terminal state.

    A state is _connected_ if it is both accessible and
    coaccessiable, i.e. if it is on a path from the initial state to a terminal
    one. Otherwise we call a state _disconnected_.
    """
    if transducer.initial is None:
        return []

    digraph: DigraphAdjacencyList = transducer.underlying_digraph()
    is_accessible: List[bool] = digraph_is_reachable(
        digraph, [transducer.initial]
    )

    digraph_rev: DigraphAdjacencyList = digraph_reverse(digraph)
    terminal_states: List[StateId] = [
        state
        for state in range(transducer.nr_states)
        if transducer.terminal[state]
    ]
    is_coaccessible = digraph_is_reachable(digraph_rev, terminal_states)

    result: List[StateId] = [
        state
        for state in range(transducer.nr_states)
        if is_accessible[state] and is_coaccessible[state]
    ]
    return result


def transducer_topological_order(
    transducer: Transducer,
) -> Optional[List[StateId]]:
    """Return the transducer states in topological order, if possible.

    We assume that our transducers are always acyclic, so this should always
    return the topological order and not `None`.

    Parameters
    ----------
    transducer: Transducer

    Returns
    -------
    Optional[List[StateId]]
        The states in topological order, if one exists, and `None` otherwise.
        The states are given by their state ids.

    See Also
    --------
    digraph_topological_order: For the analogous function for digraphs.

    Notes
    -----
    The topological order of a transducer corresponds exactly with the
    topological order of its underlying digraph.
    """
    digraph = transducer.underlying_digraph()
    return digraph_topological_order(digraph)


def transducer_induced_subtransducer(
    transducer: Transducer, states: List[StateId]
) -> Transducer:
    """Return the subtransducer induced by the given states.

    Does not modify the input transducer.

    Parameters
    ----------
    transducer: Transducer
        The base transducer.
    states: List[StateId]
        A list of states of the given transducer that will be used to generate
        the induced subtransducer.

    Returns
    -------
    Transducer
        The induced subtransducer.

    Notes
    -----
    For a given transducer and a collection of states, the subtransducer
    induced by those states is obtained by removing all of the states not in
    the collection.
    TODO: Better description, maybe a reference?
    """

    state: StateId
    included: List[bool] = [False for _ in range(transducer.nr_states)]
    for state in states:
        included[state] = True

    induced_subtransducer = Transducer(None, [], [], [])
    state_lookup: List[Optional[StateId]] = [
        None for _ in range(transducer.nr_states)
    ]
    for state in states:
        next_state = [
            child if child is not None and included[child] else None
            for child in transducer.next_state[state]
        ]
        next_letter = [
            letter if child is not None and included[child] else None
            for child, letter in zip(
                transducer.next_state[state], transducer.next_letter[state]
            )
        ]
        state_lookup[state] = induced_subtransducer.add_state(
            next_state, next_letter, transducer.terminal[state]
        )

    for state in range(induced_subtransducer.nr_states):
        for letter, child in enumerate(induced_subtransducer.next_state[state]):
            if child is not None:
                assert state_lookup[child] is not None
                induced_subtransducer.next_state[state][letter] = state_lookup[
                    child
                ]

    if transducer.initial is not None and included[transducer.initial]:
        assert state_lookup[transducer.initial] is not None
        induced_subtransducer.initial = state_lookup[transducer.initial]

    return induced_subtransducer


def transducer_trim(transducer: Transducer) -> Transducer:
    """Return the equivalent trim transducer.

    Does not modify the input.

    Parameters
    ----------
    transducer: Transducer

    Returns
    -------
    Transducer
        A trim transducer equivalent to the given one.

    See Also
    --------
    transducer_connected_states: For the definition of connectedness.

    Notes
    -----
    If a state is disconnected, then removing it does not change the function
    that the transducer realizes. _Trimming_ a transducer removes all of its
    disconnected states. A transducer whose states are all connected is called
    _trim_.
    """
    connected_states: List[StateId] = transducer_connected_states(transducer)
    return transducer_induced_subtransducer(transducer, connected_states)


def transducer_isomorphism(
    transducer1: Transducer, transducer2: Transducer
) -> bool:
    """Given two trim transducers, determine if they are isomorpic.

    Parameters
    ----------
    transducer1: Transducer
    transducer2: Transducer

    Returns
    -------
    bool
        `True` if the transducers are isomorphic and `False` otherwise.

    Notes
    -----
    Two transducers are _isomorphic_ if there exists a bijection between states
    that also preserves transitions and transition outputs.
    """
    if len(transducer_connected_states(transducer1)) != transducer1.nr_states:
        raise RuntimeError("the 1st argument (a transducer) must be connected")
    if len(transducer_connected_states(transducer2)) != transducer2.nr_states:
        raise RuntimeError("the 2nd argument (a transducer) must be connected")

    if transducer1.nr_states != transducer2.nr_states:
        return False
    if transducer1.nr_states == 0:
        # if transducer1 and transducer2 are trim and have no states, then they
        # are both the empty transducer and we can return True
        return True

    iso: List[Optional[StateId]] = [None for _ in range(transducer1.nr_states)]

    # A trim transducer without an initial state is empty, so would have
    # returned above.
    assert transducer1.initial is not None
    iso[transducer1.initial] = transducer2.initial

    que = [transducer1.initial]
    while len(que) > 0:
        state1 = que.pop()
        state2 = iso[state1]
        assert state2 is not None
        for letter, child1 in enumerate(transducer1.next_state[state1]):
            child2 = transducer2.next_state[state2][letter]
            if child1 is not None:
                if child2 is None:
                    return False
                if (
                    transducer1.next_letter[state1][letter]
                    != transducer2.next_letter[state2][letter]
                ):
                    return False

                if iso[child1] is not None and iso[child1] != child2:
                    return False
                if iso[child1] is None:
                    iso[child1] = child2
                    que.append(child1)
            elif child2 is not None:
                return False

    for state in iso:
        if state is None:
            return False

    return True


def transducer_minimize(transducer: Transducer) -> Transducer:
    """Return the minimal transducer that is equivalent to the given one.

    Does not modify the input.

    Parameters
    ----------
    transducer: Transducer

    Return
    ------
    Transducer
        The minimum transducer equivalent to the input transducer.

    Notes
    -----
    As before, we assume that our transducers are acyclic, synchronous and
    deterministic and we constrain our minimal transducer to also be acyclic,
    synchronous and deterministic, which allows us to use the automata
    minimization techniques of [1]_ to do this efficiently.

    Note that, unlike our particular case, for general transducers the problem
    of minimization is very difficult.

    Our implementation uses a dictionary to keep track of equivalent states,
    which means it is not exactly linear time. For a true linear time algorithm
    see [1]_.

    References
    ----------
    .. [1] TODO: Revuz minimization

    """
    state_tuple: Tuple[
        Tuple[Optional[StateId], ...], Tuple[Optional[OutputLetter], ...]
    ]
    state_tuple_to_representative: Dict[
        Tuple[
            Tuple[Optional[StateId], ...], Tuple[Optional[OutputLetter], ...]
        ],
        StateId,
    ]

    trim_transducer = transducer_trim(transducer)

    if trim_transducer.initial is None:
        return Transducer(None, [], [], [])

    topo_order = transducer_topological_order(trim_transducer)
    # The following assertion will always pass as our transducers are assumed
    # to be acyclic
    assert topo_order is not None

    # Representative will associate to each state_id a unique state_id
    # of a state that is equivalent to it.
    representative: List[StateId] = list(range(trim_transducer.nr_states))
    # We use a hash dictionary here which is not strictly speaking linear time,
    # however to achieve this a radix sort can be used instead as per Revuz. We
    # chose a hash dict for simplicity of implementation and good practical
    # performance.
    state_tuple_to_representative = {}
    for state in reversed(topo_order):
        state_tuple = (
            tuple(
                representative[child] if child is not None else None
                for child in trim_transducer.next_state[state]
            ),
            tuple(trim_transducer.next_letter[state]),
        )
        if state_tuple not in state_tuple_to_representative:
            state_tuple_to_representative[state_tuple] = state
        else:
            representative[state] = state_tuple_to_representative[state_tuple]

    for state in range(trim_transducer.nr_states):
        for letter, child in enumerate(trim_transducer.next_state[state]):
            if child is not None:
                trim_transducer.next_state[state][letter] = representative[
                    child
                ]

    return transducer_trim(trim_transducer)


"""
Section 4: Examples of transducers realizing f_w.

TODO: writeup
"""


def treelike_transducer(word: OutputWord) -> Transducer:
    """Return the treelike transducer associated with a word."""
    transducer: Transducer
    pref: Optional[OutputWord]
    suff: Optional[OutputWord]
    ltof: Optional[OutputLetter]
    ftol: Optional[OutputLetter]
    transducer_pref: Transducer
    transducer_suff: Transducer

    if len(word) == 0:
        transducer = Transducer(0, [[None, None]], [[None, None]], [True])
        return transducer

    pref, ltof = pref_ltof(word)
    suff, ftol = suff_ftol(word)
    assert pref is not None
    assert suff is not None
    transducer_pref = treelike_transducer(pref)
    transducer_suff = treelike_transducer(suff)

    offset_pref = 1
    offset_suff = 1 + transducer_pref.nr_states
    transducer = Transducer(None, [], [], [])
    assert transducer_pref.initial is not None
    assert transducer_suff.initial is not None
    transducer.add_state(
        [
            offset_pref + transducer_pref.initial,
            offset_suff + transducer_suff.initial,
        ],
        [ltof, ftol],
        False,
    )

    for transducer_atob, offset_atob in [
        (transducer_pref, offset_pref),
        (transducer_suff, offset_suff),
    ]:
        for state in range(transducer_atob.nr_states):
            transducer.add_state(
                [
                    offset_atob + child if child is not None else None
                    for child in transducer_atob.next_state[state]
                ],
                transducer_atob.next_letter[state],
                transducer_atob.terminal[state],
            )

    return transducer


def interval_transducer(word: OutputWord) -> Transducer:
    """TODO: description"""
    size_cont: int
    right: List[List[Optional[int]]]
    left: List[List[Optional[int]]]
    interval_lookup: Dict[Tuple[int, int], StateId]
    i: Optional[int]
    j: Optional[int]
    rr: Optional[int]
    ll: Optional[int]
    terminal: List[bool]

    size_cont = len(cont(word))
    right = [compute_right(k, word) for k in range(1, size_cont + 1)]
    left = [compute_left(k, word) for k in range(1, size_cont + 1)]

    transducer = Transducer(None, [[None, None]], [[None, None]], [True])
    # We use a hash dictionary to associate to each state representing pair
    # (i, j) the id of the state it corresponds to. This is not strictly
    # speaking linear, however a linear runtime can be achieved for example by
    # using radix sort as in the Radoszewski-Rytter paper.
    interval_lookup = {}
    for k in range(size_cont):
        for i, j in enumerate(right[k]):
            if j is not None and (i, j) not in interval_lookup:
                interval_lookup[(i, j)] = transducer.nr_states
                if k == 0:
                    transducer.add_state([0, 0], [word[i], word[i]], False)
                else:
                    rr = right[k - 1][i]
                    ll = left[k - 1][j]
                    assert rr is not None
                    assert ll is not None
                    transducer.add_state(
                        [
                            interval_lookup[(i, rr)],
                            interval_lookup[(ll, j)],
                        ],
                        [word[rr + 1], word[ll - 1]],
                        False,
                    )
        for j, i in enumerate(left[k]):
            if i is not None and (i, j) not in interval_lookup:
                # TODO: Remove duplicated code
                interval_lookup[(i, j)] = transducer.nr_states
                if k == 0:
                    transducer.add_state([0, 0], [word[i], word[i]], False)
                else:
                    rr = right[k - 1][i]
                    ll = left[k - 1][j]
                    assert rr is not None
                    assert ll is not None
                    transducer.add_state(
                        [
                            interval_lookup[(i, rr)],
                            interval_lookup[(ll, j)],
                        ],
                        [word[rr + 1], word[ll - 1]],
                        False,
                    )

    transducer.initial = interval_lookup[(0, len(word) - 1)]

    # Store the (i, j) state labels for debugging and visualization purposes
    label: List[str] = [""] * transducer.nr_states
    for interval in interval_lookup:
        i, j = interval
        label[interval_lookup[interval]] = str((i + 1, j + 1))
    label[0] = "0"

    return transducer


def transducer_precompute_q(
    state: Optional[StateId], letter: InputLetter, transducer: Transducer
) -> List[StateId]:
    """Calculate all states reachable from `state` using `letter`.

    Parameters
    ----------
    state: Optional[StateId]
    letter: InputLetter
    transducer: Transducer

    Returns
    -------
    List[StateId]
        The list of states `[q_0, q_1, q_2, ..., q_n]` where `q_0` is the
        `state`, `q_n` is a terminal state, and there is a transition from `q_i`
        into `q_{i+1}` labelled by input letter `letter`.
    """
    if state is None:
        return []
    result: List[StateId] = []
    while state is not None:
        result.append(state)
        state = transducer.next_state[state][letter]
    return result


def transducer_cont(
    state: StateId, transducer: Transducer
) -> Set[OutputLetter]:
    """Return the content of the free band element represented by `state`.

    Parameters
    ----------
    state: State
    transducer: Transducer

    Returns
    -------
    Set[OutputLetter]
    """
    q = transducer_precompute_q(state, 0, transducer)
    content: Set[OutputLetter] = set()
    for state in q:
        letter = transducer.next_letter[state][0]
        if letter is not None:
            content.add(letter)
    return content


def minimal_transducer(word: OutputWord) -> Transducer:
    """ """
    return transducer_minimize(interval_transducer(word))
