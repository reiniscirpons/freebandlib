""" Transducer visualization algorithms for freebandlib. """
from typing import Callable, List, Optional
import graphviz
import dot2tex
from freeband import OutputLetter, StateId, Transducer, TransducerState

# We use a generic parsing scheme which uses two helper functions to process
# The edge labels and node labels
NodeFunction = Callable[[StateId, bool, bool], str]
EdgeFunction = Callable[[StateId,
                         List[Optional[StateId]],
                         List[Optional[OutputLetter]]], str]

def generic_transducer_parse(transducer: Transducer,
                             header: str,
                             footer: str,
                             node_fun: NodeFunction,
                             edge_fun: EdgeFunction) -> str:
    """ A generic transducer parser for output in multiple formats.

    Args:
        transducer - the transducer to parse;
        header     - the text of the output string preceding the node and edge
        definitions;
        footer     - the text of the output string succceding the node and edge
        definitions;
        node_fun   - a function which converts node data into its output
        string representation;
        edge_fun   - a function which converts a give nodes out edge data into a
        string representation.

    Returns:
        An output string
    """
    S = [header]
    for state_id, _ in enumerate(transducer.states):
        S.append(node_fun(state_id,
                          transducer.initial==state_id,
                          transducer.terminal[state_id]))
    for state_id, state in enumerate(transducer.states):
        S.append(edge_fun(state_id, state.next_state_id(), state.next_letter))
    S.append(footer)
    return "\n".join(S)

def dot_string(transducer: Transducer,
               state_label: Optional[List[str]] = None,
               edge_label: bool = True,
               out_alphabet: Optional[List[str]] = None,
               out_colors: Optional[List[str]] = None,
               state_attrs: str = "[shape=circle]") -> str:
    """ TODO: Description
    """
    header = "digraph{\n ordering=\"out\""
    if out_colors is None:
        # If no colors were provided, default to a preset color scheme
        header += "\nedge [colorscheme=\"set19\"] "
    footer = "}"

    node_attrs = "shape=circle"
    def node_fun(state_id: StateId, is_initial: bool, is_terminal: bool) -> str:
        S = [str(state_id)]

        S.append("[")
        S.append(node_attrs)
        if state_label is not None:
            S.append(state_label[state_id])
        S.append("]")

        if is_initial:
            S.append("\ninitial [shape=none label=\"\"]")
            S.append("\ninitial -> " + str(state_id))

        if is_terminal:
            S.append("\nterminal" + str(state_id) + " [shape=none label=\"\"]")
            S.append("\n"+str(state_id) + " -> " + "terminal" + str(state_id))

        return " ".join(S)

    def edge_fun(state_id: StateId,
                 next_state_id: List[Optional[StateId]],
                 next_output_letter: List[Optional[OutputLetter]]) -> str:
        S: List[str] = []
        for in_letter, child_id in enumerate(next_state_id):
            if child_id is not None:
                out_letter = next_output_letter[in_letter]
                assert out_letter is not None
                S.append(str(state_id))
                S.append(" -> ")
                S.append(str(child_id))
                S.append("[")
                if out_colors is not None:
                    color = out_colors[out_letter]
                else:
                    color = str(out_letter+1)
                if edge_label:
                    S.append("color=" + color)
                    if out_alphabet is not None:
                        out_label = out_alphabet[out_letter]
                    else:
                        # If no out labels are given, convert number to letter,
                        # i.e.  0 -> a, 1 -> b, 2 -> c etc.
                        out_label = chr(ord("a") + out_letter)
                    S.append("label=\"" + str(in_letter) + "|" + out_label +
                                "\"")
                # Hack for tikz output
                if in_letter == 0:
                    S.append("style=\"-latex\"")
                elif in_letter == 1:
                    S.append("style=\"-latex reversed\"")
                S.append("]\n")
        return " ".join(S)

    return generic_transducer_parse(transducer, header, footer,
                                    node_fun, edge_fun)

def tikz_string(transducer: Transducer,
                codeonly=False,
                state_label: Optional[List[str]] = None,
                edge_label: bool = True,
                out_alphabet: Optional[List[str]] = None,
                out_colors: Optional[List[str]] = None,
                state_attrs: str = "[shape=circle]") -> str:
    """ Generate tikz string. 

    Uses dot2tex
    """
    docpreamble = ""
    if out_colors is None:
        # Use special default colors for tikz
        docpreamble += "\n\\colorlet{mycolor0}{black}\n"+\
                   "\\colorlet{mycolor1}{blue}\n"+\
                   "\\colorlet{mycolor2}{red}\n"+\
                   "\\colorlet{mycolor3}{blue!20!green!80!}\n"+\
                   "\\colorlet{mycolor4}{red!20!yellow!80!}\n"+\
                   "\\colorlet{mycolor5}{magenta}\n"+\
                   "\\colorlet{mycolor6}{orange}\n"+\
                   "\\colorlet{mycolor7}{cyan}\n"
        out_colors = ["mycolor"+str(i+1) for i in range(8)]

    dot = dot_string(transducer, state_label, edge_label, out_alphabet,
                     out_colors, state_attrs)
    return dot2tex.dot2tex(dot, format="tikz", texmode="math", duplicate=True,
            docpreamble=docpreamble, crop=True, codeonly=codeonly)

