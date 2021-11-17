""" Tests for algorithms implemented as part of freebandlib. """
from freeband import InputLetter, OutputLetter, StateId, TransducerState,
                     Transducer
import freeband

"""
Section 1: Type validators

This section is a counterpart to Section 1 in freeband.py. The tests here are
meant to check 
"""

def is_valid_input_letter(letter: InputLetter) -> bool:
    """ Check that the input alphabet letter constraints hold.

    An input letter is considered valid if:
        1) it is 0 or 1
    """
    return letter in (0, 1)

def is_valid_output_letter(letter: OutputLetter) -> bool:
    """ Check that the output alphabet letter constraints hold.

    An output letter is considered valid if:
        1) it is a non-negative integer
    """
    return isinstance(letter, int) and letter >= 0

def is_valid_state_id(state_id: StateId) -> bool:
    """ Check that the state id constraints hold.

    A state id is considered valid if:
        1) it is a non-negative integer
    """
    return isinstance(state_id, int) and state_id >= 0

def is_valid_transducer_state(state: TransducerState) -> bool:
    """ Check that the transducer state constraints hold.

    A transducer state is considered valid if:
        1) its letter and state transitions are defined using lists;
        2) it has letter and state transitions defined only for the input
        alphabet letters;
        3) a state transition is defined if and only if a letter transition is
        defined;
        4) every letter transition outputs a valid letter;
        5) it has a valid state id.
    Note that we do not check the child states for validity when checking the
    validity of a state. These constraints also force valid transducers to be
    deterministic and synchronous.
    """
    if not isinstance(state.next_state, list) or \
       not isinstance(state.next_letter, list) or \
       len(state.next_state) != len(state.next_letter) or \
       len(state.next_state) != 2:
        return False

    for i in [0 , 1]:
        if (state.next_state[i] is None and \
            state.next_letter[i] is not None) or \
           (state.next_state[i] is not None and \
            state.next_letter[i] is None):
            return False
        if state.next_letter[i] is not None and \
           not is_valid_output_letter(state.next_letter[i]):
            return False

    if not is_valid_state_id(state.state_id):
        return False

    return True

def is_valid_transducer(transducer: Transducer) -> bool:
    """ Check that the transducer constraints hold.

    A transducer is considered valid if:
        1) all its states are valid;
        2) each states id is equal to its position in the transducer state list;
        3) it is acyclic.
    Note that we do not require our transducers to be connected.
    """
    states = freeband.topological_order(transducer)
    if states is None:
        return False

    for i, state in enumerate(states):
        if not is_valid_transducer_state(state) or not state_id == i:
            return False
    return True
