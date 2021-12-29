""" Freebandlib: Reference implementations of algorithms for free bands. """
from __future__ import annotations
from typing import Callable, Dict, List, Optional, Set, Tuple

"""
Section 1: Types

In this section we define the types we use for our algorithms. Furthermore, we
give concrete datastructures that implement said types.

These datastructures are tailored to our specific use-case and therefore are
not intended to cover the full generality of transducer and semigroup theory.
Rather we have choosen them to allow us to implement the algorithms described
in the companion paper to this library (TODO:reference) in a fairly efficient
and understandable manner while retaining the time and space complexities from
the paper.
"""

# Throughout this implementation, we assume that our input alphabet is {0, 1}
# and our output alphabets are always sets of the form {0, 1, ..., n} for some
# n.
InputLetter = int
OutputLetter = int
OutputWord = List[OutputLetter]
InputWord = List[InputLetter]
# Each transducer state is assigned an identifier. These are required to be
# non-negative integers.
StateId = int


class TransducerState:
    """ A datastructure representing a transducer state.

    We assume that our transducers are synchronous and deterministic, so that
    no epsilon transitions are permitted, and each input letter leads to
    exactly one state, and outputs exactly one output letter.

    Since the input alphabet is always {0, 1}, we opt to store our state
    transition and letter transition functions as lists, where the i-th entry
    corresponds to the transition upon reading i (if this transition is defined
    and None otherwise).

    Attributes:
        state_id: the identifier associated to this state
        next_state: the state transition function
        next_letter: the letter transition function
    """
    def __init__(self,
                 state_id: StateId,
                 next_state: List[Optional[TransducerState]],
                 next_letter: List[Optional[OutputLetter]]):
        self.state_id = state_id
        self.next_state = next_state
        self.next_letter = next_letter

    def __repr__(self):
        return repr((self.state_id, self.next_state_id(), self.next_letter))

    def next_state_id(self) -> List[Optional[StateId]]:
        """ Return the next state function in terms of state ids. """
        return [state.state_id if state is not None else None
                for state in self.next_state]


class Transducer:
    """ A datastructure representing a transducer.

    As before, we assume that our transducers are synchronous and
    deterministic.  In addition we assume that our transducers are acyclic.
    This implies the function they realize have a finite domain but is a
    stronger condition.

    We implement transducers as a collection of states along with a pointer to
    the initial states and a boolean list indicating if a state is terminal or
    not. We require that each state of a transducer has a unique state id
    within the transducer. Furthermore in implementation, the state id
    corresponds to the states position in the state collection.

    Attributes:
        initial: the id of the initial state
        states: a list containing all the transducer states
        terminal: a list indicating if the i-th state is terminal or not
        label: a list of node labels. These are optional and only serve a
        purpose for debugging or visualising
    """
    def __init__(self,
                 initial: Optional[StateId],
                 states: List[TransducerState],
                 terminal: List[bool],
                 label: List[str] = None):
        self.initial = initial
        self.states = states
        self.terminal = terminal
        self.label = label
        self.normalize()

    def __repr__(self):
        return repr((self.initial, self.states, self.terminal))

    def normalize(self):
        """ Number states in consecutive order. """
        for i, state in enumerate(self.states):
            state.state_id = i

    def add_state(self,
                  next_state_id: List[StateId],
                  next_letter: List[Optional[OutputLetter]],
                  is_terminal: bool) -> TransducerState:
        """ Add a state to the transducer.

        This method modifies the transducer to have a new state with properties
        specified by the arguments.

        Args:
            next_state_id: a state transition function given by specifying the
            id of the next state for each input symbol instead of the actual
            state itself.
            next_letter: a letter transition function.
            is_terminal: a boolean indicating if the state is terminal.

        Returns:
            The state that was added to the transducer.
        """
        self.states.append(TransducerState(
            len(self.states),
            [self.states[i] for i in next_state_id],
            next_letter))
        self.terminal.append(is_terminal)
        return self.states[-1]

    def traverse(self, word: InputWord) -> Optional[OutputWord]:
        """ Traverse an input word through the trasducer and return its output.

        Args:
            word: an input word to traverse.

        Returns:
            The output word corresponding to the input, if a terminal state is
            reached while traversing the input word and None otherwise.
        """
        state: Optional[TransducerState]
        result_letter: Optional[OutputLetter]
        result: OutputWord

        if self.initial is None:
            return None
        state = self.states[self.initial]
        if state is None:
            return None

        result = []
        for letter in word:
            assert state is not None
            result_letter = state.next_letter[letter]
            if result_letter is None:
                return None
            result.append(result_letter)
            state = state.next_state[letter]

        if state is None or not self.terminal[state.state_id]:
            return None

        return result

    def underlying_digraph(self) -> DigraphAdjacencyList:
        """ Return the underlying graph of the transducer.

        Every transducer has an underlying digraph structure whose vertices are
        given by states and there is an edge from one vertex to another if
        there is a state transition between the corresponding states.

        Returns:
            The adjacency list of the underlying graph of the transducer.
        """
        result: DigraphAdjacencyList
        state: TransducerState
        state_id: Optional[StateId]

        result = [[] for _ in self.states]
        for state in self.states:
            for state_id in state.next_state_id():
                if state_id is not None and \
                   state_id not in result[state.state_id]:
                    result[state.state_id].append(state_id)

        return result


"""
Section 2: Basic operations on transducers.

TODO: writeup
"""


def transducer_connected_states(transducer: Transducer) -> List[StateId]:
    """ Return all the connected state ids of a given transducer.

    Recall that a transducer state is connected if it is on a path from an
    initial state to a terminal one.

    Args:
        transducer

    Returns:
        A collection of state ids such that each state is on a path from the
        initial state to a terminal state.
    """
    if transducer.initial is None:
        return []

    nr_states = len(transducer.states)
    underlying_digraph = transducer.underlying_digraph()
    is_accessible = digraph_is_reachable(underlying_digraph,
                                         [transducer.initial])
    is_coaccessible = digraph_is_reachable(digraph_reverse(underlying_digraph),
                                           [state_id for state_id
                                            in range(nr_states)
                                            if transducer.terminal[state_id]])

    result = [state_id for state_id in range(nr_states)
              if is_accessible[state_id] and is_coaccessible[state_id]]
    return result


def transducer_topological_order(transducer: Transducer) -> \
        Optional[List[StateId]]:
    """ Return the transducer states in topological order, if possible.

    We say that the states are in topological order if they are in the digraph
    sense with respect to the underlying digraph of the transducer

    We assume that our transducers are always acyclic, so this should always
    return the topological order. For more info see
    `digraph_topological_order`.

    Args:
        transducer: The transducer to order

    Returns:
        The states in topological order, if one exists, and None otherwise.
    """
    return digraph_topological_order(transducer.underlying_digraph())


def transducer_induced_subtransducer(transducer: Transducer,
                                     state_ids: List[StateId]) -> Transducer:
    """
    """
    initial: Optional[StateId]
    states: List[TransducerState]
    terminal: List[bool]
    included: List[bool]
    state: TransducerState
    child: Optional[TransducerState]
    letter: InputLetter
    state_id: StateId

    included = [False for _ in transducer.states]
    for state_id in state_ids:
        included[state_id] = True

    states = [transducer.states[state_id] for state_id in state_ids]
    for state in states:
        for letter, child in enumerate(state.next_state):
            if child is not None and not included[child.state_id]:
                state.next_state[letter] = None
                state.next_letter[letter] = None

    terminal = [transducer.terminal[state_id] for state_id in state_ids]

    if transducer.initial is not None and included[transducer.initial]:
        initial = state_ids.index(transducer.initial)
    else:
        initial = None

    return Transducer(initial, states, terminal)


def transducer_trim(transducer: Transducer) -> Transducer:
    """
    """
    return transducer_induced_subtransducer(transducer,
                                            transducer_connected_states(
                                                transducer))


def transducer_isomorphism(transducer1: Transducer,
                           transducer2: Transducer) -> bool:
    """ Given two trim transducers, determine if they are isomorpic.
    """
    iso: List[Optional[StateId]]

    if len(transducer1.states) == len(transducer2.states):
        return False

    if len(transducer1.states) == 0:
        return True

    if transducer1.initial is None or transducer2.initial is None:
        return False

    iso = [None for _ in transducer1.states]

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
                if iso[child1.state_id] is not None and \
                   iso[child1.state_id] != child2.state_id:
                    return False
                if iso[child1.state_id] is None:
                    iso[child1.state_id] = child2.state_id
                    que.append(child1)
            elif child2 is not None:
                return False

    for state_id1, state_id2 in enumerate(iso):
        if state_id2 is None:
            return False

    return True


def transducer_minimize(transducer: Transducer) -> Transducer:
    """
    """
    trim_transducer: Transducer
    topo_order: Optional[List[StateId]]
    nr_states: int
    representative: List[StateId]
    state_tuple: Tuple[Tuple[Optional[StateId], ...],
                       Tuple[Optional[OutputLetter], ...]]
    state_tuple_to_representative: Dict[Tuple[Tuple[Optional[StateId],
                                                    ...],
                                              Tuple[Optional[OutputLetter],
                                                    ...]
                                              ],
                                        StateId]
    state: TransducerState
    child: Optional[TransducerState]
    letter: InputLetter
    state_id: StateId

    trim_transducer = transducer_trim(transducer)

    if trim_transducer.initial is None:
        return Transducer(None, [], [])

    nr_states = len(trim_transducer.states)
    topo_order = transducer_topological_order(trim_transducer)
    assert topo_order is not None

    # Representative will associate to each state_id a unique state_id
    # of a state that is equivalent to it.
    representative = list(range(nr_states))
    # We use a hash dictionary here which is not strictly speaking linear time,
    # however to achieve this a radix sort can be used instead as per Revuz. We
    # chose a hash dict for simplicity of implementation and good practical
    # performance.
    state_tuple_to_representative = {}
    for state_id in reversed(topo_order):
        state = trim_transducer.states[state_id]
        state_tuple = (tuple(representative[child_id] if child_id is not None
                             else None for child_id in state.next_state_id()),
                       tuple(state.next_letter))
        if state_tuple not in state_tuple_to_representative:
            state_tuple_to_representative[state_tuple] = state_id
        else:
            representative[state_id] = \
                state_tuple_to_representative[state_tuple]

    for state_id, state in enumerate(trim_transducer.states):
        for letter, child in enumerate(state.next_state):
            if child is not None:
                state.next_state[letter] = \
                    trim_transducer.states[representative[child.state_id]]

    return transducer_trim(trim_transducer)


"""
Section 3: Basic operations on words.

TODO: writeup
"""


def cont(word: OutputWord) -> Set[OutputLetter]:
    """ Return the content of a word. """
    return set(word)


def pref_ltof(word: OutputWord) -> Tuple[Optional[OutputWord],
                                         Optional[OutputLetter]]:
    """ Return the prefix and first to occur last letter of a word. """
    k = len(cont(word))
    j = 0
    seen = set()
    for i, letter in enumerate(word):
        if letter not in seen:
            j += 1
            if j == k:
                return word[:i], letter
            seen.add(letter)
    # Only happens if word is the empty word
    return None, None


def suff_ftol(word: OutputWord) -> Tuple[Optional[OutputWord],
                                         Optional[OutputLetter]]:
    """ Return the suffix and last to occur first letter of a word. """
    return pref_ltof(list(reversed(word)))


def word_function(word: OutputWord) -> Callable[[InputWord],
                                                Optional[OutputWord]]:
    """ Given a word w return return its associated function f_w. """
    def f_w(input_word: InputWord) -> Optional[OutputWord]:
        result: OutputWord
        current_part: Optional[OutputWord]
        output_letter: Optional[OutputLetter]

        result = []
        current_part = word

        for input_letter in input_word:
            if current_part is None:
                return None
            if input_letter == 0:
                current_part, output_letter = pref_ltof(current_part)
            elif input_letter == 1:
                current_part, output_letter = suff_ftol(current_part)
            assert output_letter is not None
            result.append(output_letter)

        if current_part is None:
            return None
        if len(current_part) == 0:
            return result
        return None

    return f_w


def compute_right(k: int, w: OutputWord) -> List[Optional[int]]:
    """ TODO: description
    """
    curr_cont: List[int]
    curr_k: int
    right_k: List[Optional[int]]
    i: int
    j: int

    curr_cont = [0 for _ in range(max(w) + 1)]
    curr_k = 0
    right_k = [None for _ in range(len(w))]
    j = -1
    for i in range(len(w)):
        if i > 0:
            curr_cont[w[i - 1]] -= 1
            if curr_cont[w[i - 1]] == 0:
                curr_k -= 1
        while j < len(w) - 1 and (curr_cont[w[j + 1]] != 0 or curr_k < k):
            j += 1
            if curr_cont[w[j]] == 0:
                curr_k += 1
            curr_cont[w[j]] += 1
        if curr_k == k:
            right_k[i] = j
    return right_k


def compute_left(k: int, w: OutputWord) -> List[Optional[int]]:
    """ TODO: description
    """
    result = [None if x is None else len(w) - 1 - x
              for x in compute_right(k, list(reversed(w)))]
    return list(reversed(result))


"""
Section 4: Examples of transducers realizing f_w.

TODO: writeup
"""


def treelike_transducer(word: OutputWord) -> Transducer:
    """ Return the treelike transducer associated with a word. """
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
        transducer = Transducer(0,
                                [TransducerState(0,
                                                 [None, None],
                                                 [None, None])],
                                [True])
        return transducer

    pref, ltof = pref_ltof(word)
    suff, ftol = suff_ftol(word)
    assert pref is not None
    assert suff is not None
    transducer_pref = treelike_transducer(pref)
    transducer_suff = treelike_transducer(suff)
    assert transducer_pref.initial is not None
    assert transducer_suff.initial is not None

    states = [TransducerState(0,
                              [transducer_pref.states[transducer_pref.initial],
                               transducer_suff.states[transducer_suff.initial]
                               ],
                              [ltof, ftol])]
    states.extend(transducer_pref.states)
    states.extend(transducer_suff.states)
    terminal = [False]
    terminal.extend(transducer_pref.terminal)
    terminal.extend(transducer_suff.terminal)
    transducer = Transducer(0, states, terminal)
    return transducer


def interval_transducer(word: OutputWord) -> Transducer:
    """ TODO: description
    """
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
                    states.append(TransducerState(len(states),
                                                  [states[0], states[0]],
                                                  [word[i], word[i]]))
                else:
                    rr = right[k - 1][i]
                    ll = left[k - 1][j]
                    assert rr is not None
                    assert ll is not None
                    states.append(TransducerState(len(states),
                                  [states[interval_lookup[(i, rr)]],
                                   states[interval_lookup[(ll, j)]]],
                                  [word[rr + 1], word[ll - 1]]))
        for j, i in enumerate(left[k]):
            if i is not None and (i, j) not in interval_lookup:
                # TODO: Remove duplicated code
                interval_lookup[(i, j)] = len(states)
                if k == 0:
                    states.append(TransducerState(len(states),
                                                  [states[0], states[0]],
                                                  [word[i], word[i]]))
                else:
                    rr = right[k - 1][i]
                    ll = left[k - 1][j]
                    assert rr is not None
                    assert ll is not None
                    states.append(TransducerState(len(states),
                                  [states[interval_lookup[(i, rr)]],
                                   states[interval_lookup[(ll, j)]]],
                                  [word[rr + 1], word[ll - 1]]))

    initial = interval_lookup[(0, len(word) - 1)]
    terminal = [False for _ in range(len(states))]
    terminal[0] = True

    # Store the (i, j) state labels for debugging and visualization purposes
    label: List[str] = ["" for _ in range(len(states))]
    for interval in interval_lookup:
        i, j = interval
        label[interval_lookup[interval]] = str((i + 1, j + 1))
    label[0] = "0"

    return Transducer(initial, states, terminal, label)


def minimal_transducer(word: OutputWord) -> Transducer:
    """
    """
    return transducer_minimize(interval_transducer(word))


"""
Section 5: Equality checking

TODO: writeup
"""


def equivalent_words(word1: OutputWord, word2: OutputWord) -> bool:
    """
    """
    return transducer_isomorphism(minimal_transducer(word1),
                                  minimal_transducer(word2))


def equivalent_transducers(transducer1: Transducer,
                           transducer2: Transducer) -> bool:
    """
    """
    return transducer_isomorphism(transducer_minimize(transducer1),
                                  transducer_minimize(transducer2))


"""
Section 6: Multiplication

TODO: writeup
"""

"""
Section 7: Minimal word representative

TODO: writeup
"""

"""
Section 8: Graph utility functions


"""

DigraphVertex = int
DigraphAdjacencyList = List[List[DigraphVertex]]


def digraph_reverse(digraph: DigraphAdjacencyList) -> DigraphAdjacencyList:
    """ Return the adjacency list of the reverse digraph.

    The reverse digraph of a digraph has the same set of vertices but has an
    edge from u to v iff the original graph has an edge from v to u, i.e. all
    the edges are reversed.

    Args:
        digraph: The digraph to reverse

    Returns:
        An adjacency list of the reverse digraph
    """

    result: DigraphAdjacencyList
    row: List[DigraphVertex]
    u: DigraphVertex
    v: DigraphVertex

    result = [[] for _ in digraph]
    for u, row in enumerate(digraph):
        for v in row:
            result[v].append(u)

    return result


def digraph_is_reachable(digraph: DigraphAdjacencyList,
                         start: List[DigraphVertex]) -> List[bool]:
    """ Determine for every vertex if it can be reached from any start vertex.

    A vertex v is reachable from a vertex u if there is a directed path
    starting at u and ending in v. Performs a simple breadth first traversal.

    Args:
        digraph: An adjacencyy list of the underlying digraph
        start: The list of starting vertices.

    Returns:
        A boolean list seen such that seen[v] is true if and only if vertex v
        is reachable from some vertex in start.
    """
    que: List[DigraphVertex]
    seen: List[bool]
    i: int
    u: DigraphVertex
    v: DigraphVertex

    i = 0
    seen = [False for _ in digraph]
    for u in start:
        seen[u] = True
    que = start
    while i < len(que):
        u = que[i]
        for v in digraph[u]:
            if not seen[v]:
                que.append(v)
                seen[v] = True
        i += 1

    return seen


def digraph_topological_order(digraph: DigraphAdjacencyList) -> \
        Optional[List[DigraphVertex]]:
    """ Return the digraph vertices in topological order, if possible.

    We say that the vertices are in topological order if no child vertex occurs
    before its parent in the list. the function returns None if a topological
    order does not exist (i.e. there is a directed cycle).

    Args:
        digraph: An adjacency list

    Returns:
        A list of vertices in topological order, if one exists,
        and None otherwise.
    """
    topo_order: List[DigraphVertex]
    time_seen: List[int]
    row: List[DigraphVertex]
    u: DigraphVertex
    v: DigraphVertex
    i: int
    t: int

    time_seen = [0 for _ in digraph]
    for u, row in enumerate(digraph):
        for v in row:
            time_seen[v] += 1

    topo_order = [u for u, t in enumerate(time_seen) if t == 0]
    i = 0
    while i < len(topo_order):
        u = topo_order[i]
        for v in digraph[u]:
            time_seen[v] -= 1
            if time_seen[v] == 0:
                topo_order.append(v)
        i += 1

    if len(topo_order) != len(digraph):
        return None

    return topo_order
