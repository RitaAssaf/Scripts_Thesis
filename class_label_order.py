class LabelOrder:
	def __init__(self, name, label, neighbors_labels, nodes, preceds, predecessors=None, successors=None):
		self._name = name
		self._label = label
		self._neighbors_labels = neighbors_labels
		self._nodes = nodes
		self._preceds=preceds
		self._predecessors = predecessors if predecessors is not None else set()
		self._successors = successors if successors is not None else set()
		
	def __str__(self):
	
		if len(self._predecessors) > 0 or len(self._successors) > 0:
			return (
					f"{self._name}: "
					f"{self._label}.{{{', '.join(map(str, self._predecessors))}}}.{{{', '.join(map(str, self._successors))}}} "
					f" nodes: {{{', '.join(map(str, self._nodes))}}}"
					f"  preceds: {{{', '.join(map(str, self._preceds))}}}"
					)
		else:
			return (
					f"{self._name}: "
					f"{self._label}.{{{', '.join(map(str, self._neighbors_labels))}}}"
					f" nodes: {{{', '.join(map(str, self._nodes))}}}"
					f"  preceds: {{{', '.join(map(str, self._preceds))}}}")

	def add_node(self, value):
		self._nodes.append(value)