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


class TransducerState:
    """A datastructure representing a transducer state.

    Parameters
    ----------
    state_id: StateId
        The identifier associated to this state
    next_state: NextState
        The state transition function
    next_letter: List[letter]
        The letter transition function

    Notes
    -----
    We assume that our transducers are synchronous and deterministic, so that
    no epsilon transitions are permitted, and each input letter leads to
    exactly one state, and outputs exactly one output letter.

    Since the input alphabet is always :math:`{0, 1}`, we opt to store our
    state transition and letter transition functions as lists, where the
    :math:`i`-th entry corresponds to the transition upon reading :math:`i` (if
    this transition is defined and `None` otherwise).
    """

    def __init__(
        self, state_id: StateId, next_state: NextState, next_letter: NextLetter
    ):
        self.state_id = state_id
        self.next_state = next_state
        self.next_letter = next_letter

    def __repr__(self):
        """Generate a textual representation of the state."""
        return repr((self.state_id, self.next_state_id(), self.next_letter))

    def next_state_id(self) -> NextStateId:
        """Return the next state function in terms of state ids."""
        return [
            state.state_id if state is not None else None
            for state in self.next_state
        ]


# Utility types for state transitions.
NextState = List[Optional[TransducerState]]
NextStateId = List[Optional[StateId]]
NextLetter = List[Optional[OutputLetter]]


class Transducer:
    """A datastructure representing a transducer.

    Parameters
    ----------
    initial: Optional[StateId]
        The the position of the initial state in the `states` list.
        Can be `None` to support empty transducer.
    states: List[TransducerState]
        A list containing all the transducer states.
    terminal: List[bool]
        A list indicating if the `i`-th state is terminal or not.

    Other Parameters
    ----------------
    label: List[str], default=None
        A list of node labels. These are optional and only serve a purpose for
        debugging or visualising.

    See Also
    --------
    TransducerState: The constituent states of the transducer.

    Notes
    -----
    As before, we assume that our transducers are synchronous and
    deterministic. In addition we assume that our transducers are acyclic. This
    implies the function they realize have a finite domain but is a stronger
    condition.

    We implement transducers as a collection of states along with a pointer to
    the initial states and a boolean list indicating if a state is terminal or
    not. We require that each state of a transducer has a unique state id
    within the transducer. Furthermore in implementation, the state id
    corresponds to the states position in the state collection.
    """

    def __init__(
        self,
        initial: Optional[StateId],
        states: List[TransducerState],
        terminal: List[bool],
        label: List[str] = None,
    ):
        self.initial = initial
        self.states = states
        self.terminal = terminal
        self.label = label
        self.validate()  # TODO(RC) not sure if you want this here!
        self.normalize()

    def copy(self) -> Transducer:
        states = [
            TransducerState(x.state_id, [None] * 2, x.next_letter[::])
            for x in self.states
        ]
        for i, old_state in enumerate(self.states):
            states[i].next_state = [
                states[x.state_id] if x is not None else None
                for x in old_state.next_state
            ]

        return Transducer(
            self.initial,
            states,
            self.terminal[::],
            self.label[::] if self.label is not None else None,
        )

    def validate(self):
        if not (self.initial is None or isinstance(self.initial, StateId)):
            raise RuntimeError("self.initial must be None or a StateId")
        if self.initial is not None and (
            self.initial >= len(self.states) or self.initial < 0
        ):
            raise RuntimeError(
                f"self.initial must be in the range [0, {len(self.states)}"
            )
        if not (
            isinstance(self.states, List)
            and all(isinstance(x, TransducerState) for x in self.states)
        ):
            raise RuntimeError(
                "self.states must be a list of TransducerState objects"
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
        if len(self.states) != len(self.terminal):
            raise RuntimeError(
                "self.states and self.terminal must have equal length"
            )
        if self.label is not None and len(self.states) != len(self.label):
            raise RuntimeError(
                "self.states and self.label must have equal length"
            )

    def __repr__(self):
        """Generate a textual representation of the transducer."""
        return repr((self.initial, self.states, self.terminal))

    def normalize(self):
        """Make state ids correspond to position is state list."""
        for i, state in enumerate(self.states):
            state.state_id = i

    def add_state(
        self,
        next_state_id: List[StateId],
        next_letter: List[Optional[OutputLetter]],
        is_terminal: bool,
    ) -> TransducerState:
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
        TransducerState
            The state that was added to the transducer.
        """
        self.states.append(
            TransducerState(
                len(self.states),
                [self.states[i] for i in next_state_id],
                next_letter,
            )
        )
        self.terminal.append(is_terminal)
        return self.states[-1]

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
        state: Optional[TransducerState] = self.states[self.initial]

        result: OutputWord = []
        for letter in word:
            assert state is not None
            result_letter: Optional[OutputLetter] = state.next_letter[letter]
            if result_letter is None:
                return None
            result.append(result_letter)
            state = state.next_state[letter]

        if state is None or not self.terminal[state.state_id]:
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
        state: TransducerState
        state_id: Optional[StateId]

        result: DigraphAdjacencyList = [[] for _ in self.states]
        for state in self.states:
            for state_id in state.next_state_id():
                if (
                    state_id is not None
                    and state_id not in result[state.state_id]
                ):
                    result[state.state_id].append(state_id)

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

    nr_states: int = len(transducer.states)

    digraph: DigraphAdjacencyList = transducer.underlying_digraph()
    is_accessible: List[bool] = digraph_is_reachable(
        digraph, [transducer.initial]
    )

    digraph_rev: DigraphAdjacencyList = digraph_reverse(digraph)
    terminal_states: List[StateId] = [
        state_id
        for state_id in range(nr_states)
        if transducer.terminal[state_id]
    ]
    is_coaccessible = digraph_is_reachable(digraph_rev, terminal_states)

    result: List[StateId] = [
        state_id
        for state_id in range(nr_states)
        if is_accessible[state_id] and is_coaccessible[state_id]
    ]  # noqa: W503
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
    transducer: Transducer, state_ids: List[StateId]
) -> Transducer:
    """Return the subtransducer induced by the given states.

    Does not modify the input transducer.

    Parameters
    ----------
    transducer: Transducer
        The base transducer.
    state_ids: List[StateId]
        A list of states of the given transducer that will be used to generate
        the induced subtransducer. The states are given by their ids.

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
    transducer = transducer.copy()
    state_id: StateId
    included: List[bool] = [False for _ in transducer.states]
    for state_id in state_ids:
        included[state_id] = True

    state: TransducerState
    letter: InputLetter
    child: Optional[TransducerState]
    states: List[TransducerState] = [
        transducer.states[state_id] for state_id in state_ids
    ]
    for state in states:
        for letter, child in enumerate(state.next_state):
            if child is not None and not included[child.state_id]:
                state.next_state[letter] = None
                state.next_letter[letter] = None

    terminal: List[bool] = [
        transducer.terminal[state_id] for state_id in state_ids
    ]

    initial: Optional[StateId]
    if transducer.initial is not None and included[transducer.initial]:
        initial = state_ids.index(transducer.initial)
    else:
        initial = None

    return Transducer(initial, states, terminal)


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
    if len(transducer_connected_states(transducer1)) != len(transducer1.states):
        raise RuntimeError("the 1st argument (a transducer) must be connected")
    if len(transducer_connected_states(transducer2)) != len(transducer2.states):
        raise RuntimeError("the 2nd argument (a transducer) must be connected")

    if len(transducer1.states) != len(transducer2.states):
        return False
    if len(transducer1.states) == 0:
        # if transducer1 and transducer2 are trim and have no states, then they
        # are both the empty transducer and we can return True
        return True

    iso: List[Optional[StateId]] = [None for _ in transducer1.states]

    # A trim transducer without an initial state is empty, so would have
    # returned above.
    assert transducer1.initial is not None
    iso[transducer1.initial] = transducer2.initial

    que = [transducer1.states[transducer1.initial]]
    while len(que) > 0:
        state1 = que.pop()
        state_id2 = iso[state1.state_id]
        assert state_id2 is not None
        state2 = transducer2.states[state_id2]
        for input_letter, child1 in enumerate(state1.next_state):
            child2 = state2.next_state[input_letter]
            if child1 is not None:
                if child2 is None:
                    return False
                if (
                    state1.next_letter[input_letter]
                    != state2.next_letter[input_letter]
                ):
                    return False

                if (
                    iso[child1.state_id] is not None
                    and iso[child1.state_id] != child2.state_id
                ):
                    return False
                if iso[child1.state_id] is None:
                    iso[child1.state_id] = child2.state_id
                    que.append(child1)

            elif child2 is not None:
                return False

    for state_id2 in iso:
        if state_id2 is None:
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

    trim_transducer: Transducer = transducer_trim(transducer)

    if trim_transducer.initial is None:
        return Transducer(None, [], [])

    nr_states: int = len(trim_transducer.states)
    topo_order: Optional[List[StateId]] = transducer_topological_order(
        trim_transducer
    )
    # The following assertion will always pass as our transducers are assumed
    # to be acyclic
    assert topo_order is not None

    state: TransducerState
    state_id: StateId
    child_id: StateId
    # Representative will associate to each state_id a unique state_id
    # of a state that is equivalent to it.
    representative: List[StateId] = list(range(nr_states))
    # We use a hash dictionary here which is not strictly speaking linear time,
    # however to achieve this a radix sort can be used instead as per Revuz. We
    # chose a hash dict for simplicity of implementation and good practical
    # performance.
    state_tuple_to_representative = {}
    for state_id in reversed(topo_order):
        state = trim_transducer.states[state_id]
        state_tuple = (
            tuple(
                representative[child_id] if child_id is not None else None
                for child_id in state.next_state_id()
            ),
            tuple(state.next_letter),
        )
        if state_tuple not in state_tuple_to_representative:
            state_tuple_to_representative[state_tuple] = state_id
        else:
            representative[state_id] = state_tuple_to_representative[
                state_tuple
            ]

    child: Optional[TransducerState]
    letter: InputLetter
    for state_id, state in enumerate(trim_transducer.states):
        for letter, child in enumerate(state.next_state):
            if child is not None:
                state.next_state[letter] = trim_transducer.states[
                    representative[child.state_id]
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
    states: List[TransducerState]
    terminal: List[bool]

    if len(word) == 0:
        transducer = Transducer(
            0, [TransducerState(0, [None, None], [None, None])], [True]
        )
        return transducer

    pref, ltof = pref_ltof(word)
    suff, ftol = suff_ftol(word)
    assert pref is not None
    assert suff is not None
    transducer_pref = treelike_transducer(pref)
    transducer_suff = treelike_transducer(suff)
    assert transducer_pref.initial is not None
    assert transducer_suff.initial is not None

    states = [
        TransducerState(
            0,
            [
                transducer_pref.states[transducer_pref.initial],
                transducer_suff.states[transducer_suff.initial],
            ],
            [ltof, ftol],
        )
    ]
    states.extend(transducer_pref.states)
    states.extend(transducer_suff.states)
    terminal = [False]
    terminal.extend(transducer_pref.terminal)
    terminal.extend(transducer_suff.terminal)
    transducer = Transducer(0, states, terminal)
    return transducer


def interval_transducer(word: OutputWord) -> Transducer:
    """TODO: description"""
    size_cont: int
    right: List[List[Optional[int]]]
    left: List[List[Optional[int]]]
    states: List[TransducerState]
    interval_lookup: Dict[Tuple[int, int], StateId]
    i: Optional[int]
    j: Optional[int]
    rr: Optional[int]
    ll: Optional[int]
    terminal: List[bool]

    size_cont = len(cont(word))
    right = [compute_right(k, word) for k in range(1, size_cont + 1)]
    left = [compute_left(k, word) for k in range(1, size_cont + 1)]

    states = [TransducerState(0, [None, None], [None, None])]
    # We use a hash dictionary to associate to each state representing pair
    # (i, j) the id of the state it corresponds to. This is not strictly
    # speaking linear, however a linear runtime can be achieved for example by
    # using radix sort as in the Radoszewski-Rytter paper.
    interval_lookup = {}
    for k in range(size_cont):
        for i, j in enumerate(right[k]):
            if j is not None and (i, j) not in interval_lookup:
                interval_lookup[(i, j)] = len(states)
                if k == 0:
                    states.append(
                        TransducerState(
                            len(states),
                            [states[0], states[0]],
                            [word[i], word[i]],
                        )
                    )
                else:
                    rr = right[k - 1][i]
                    ll = left[k - 1][j]
                    assert rr is not None
                    assert ll is not None
                    states.append(
                        TransducerState(
                            len(states),
                            [
                                states[interval_lookup[(i, rr)]],
                                states[interval_lookup[(ll, j)]],
                            ],
                            [word[rr + 1], word[ll - 1]],
                        )
                    )
        for j, i in enumerate(left[k]):
            if i is not None and (i, j) not in interval_lookup:
                # TODO: Remove duplicated code
                interval_lookup[(i, j)] = len(states)
                if k == 0:
                    states.append(
                        TransducerState(
                            len(states),
                            [states[0], states[0]],
                            [word[i], word[i]],
                        )
                    )
                else:
                    rr = right[k - 1][i]
                    ll = left[k - 1][j]
                    assert rr is not None
                    assert ll is not None
                    states.append(
                        TransducerState(
                            len(states),
                            [
                                states[interval_lookup[(i, rr)]],
                                states[interval_lookup[(ll, j)]],
                            ],
                            [word[rr + 1], word[ll - 1]],
                        )
                    )

    initial = interval_lookup[(0, len(word) - 1)]
    terminal = [False for _ in range(len(states))]
    terminal[0] = True

    # Store the (i, j) state labels for debugging and visualization purposes
    label: List[str] = [""] * len(states)
    for interval in interval_lookup:
        i, j = interval
        label[interval_lookup[interval]] = str((i + 1, j + 1))
    label[0] = "0"

    return Transducer(initial, states, terminal, label)


def transducer_precompute_q(
    transducer: Transducer, letter: InputLetter
) -> List[StateId]:
    """Given a transducer and letter, repeatedly transition along the letter.

    Parameters
    ----------
    transducer: Transducer
    letter: InputLetter

    Returns
    -------
    List[StateId]
        The list of states `[q_0, q_1, q_2, ..., q_n]` where `q_0` is the
        initial state of `transducer` and there is a transition from `q_i`
        into `q_{i+1}` labelled by input letter `letter`.
    """
    if transducer.initial is None:
        return []

    state: Optional[TransducerState] = transducer.states[transducer.initial]
    result: List[StateId] = []
    while state is not None:
        result.append(state.state_id)
        state = state.next_state[letter]
    return result


def transducer_cont(transducer: Transducer) -> Set[OutputLetter]:
    """Return the content of the free band element represented by `transducer`.

    Parameters
    ----------
    transducer: Transducer

    Returns
    -------
    Set[OutputLetter]
    """
    q = transducer_precompute_q(transducer, 0)
    content = set()
    for state_id in q:
        state = transducer.states[state_id]
        if state.next_letter[0] is not None:
            content.add(state.next_letter[0])
    return content


def minimal_transducer(word: OutputWord) -> Transducer:
    """ """
    return transducer_minimize(interval_transducer(word))
