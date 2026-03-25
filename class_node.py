class Node:
    def __init__(self, name, label="", neighbors_labels=None, domain=None, ispattern=0, predecessors=None, successors=None):
        self._name = name
        self._label = label
        self._neighbors_labels = neighbors_labels if neighbors_labels is not None else []
        self._domain = domain if domain is not None else []
        self._ispattern = ispattern
        self._predecessors = predecessors if predecessors is not None else set()
        self._successors = successors if successors is not None else set()
    def __str__(self):
        if self._label is not None:  # Explicitly check for None
            alpha = "\u03B1"
            result = f"{alpha}({self._name}): "
            if len(self._predecessors) > 0 or len(self._successors) > 0:
                result += f"{self._label}.{{{', '.join(map(str, self._predecessors))}}}.{{{', '.join(map(str, self._successors))}}} "
            else:
                if len(self._neighbors_labels) > 0:
                    result += f"{self._label}.{{{', '.join(map(str, self._neighbors_labels))}}} "
                else:
                    result += f"{self._label} "
        else:
            result = f"{self._name}: "
        
        if self._ispattern:
            result += f", dom(x_{self._name})= & {{{', '.join(map(str, self._domain))}}}"
        
        return result
