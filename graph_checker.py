import networkx as nx
import re

def read_dot_file(filename):
    with open(filename, 'r') as f:
        return f.read()

def write_dot_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

def rename_nodes(dot_content):
    graph = nx.nx_pydot.read_dot(dot_content)
    
    # Extract existing nodes and sort them to create a mapping
    old_nodes = sorted(graph.nodes(), key=lambda n: int(n))  # Sort numerically
    node_mapping = {old: str(i + 1) for i, old in enumerate(old_nodes)}
    
    # Create a new graph with renamed nodes
    new_graph = nx.DiGraph()
    for old_node in old_nodes:
        new_graph.add_node(node_mapping[old_node], label=node_mapping[old_node])
    
    for edge in graph.edges():
        new_graph.add_edge(node_mapping[edge[0]], node_mapping[edge[1]])
    
    return nx.nx_pydot.to_pydot(new_graph).to_string()

def process_dot_file(input_file, output_file):
    dot_content = read_dot_file(input_file)
    new_dot_content = rename_nodes(dot_content)
    write_dot_file(output_file, new_dot_content)
    print(f"Processed DOT file saved as: {output_file}")

# Example usage:
# process_dot_file('input.dot', 'output.dot')
