import networkx as nx
import pydot

def read_dot_file(filename):
    with open(filename, 'r') as f:
        return f.read()

def write_dot_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

def rename_nodes(dot_content):
    graphs = pydot.graph_from_dot_data(dot_content)
    if not graphs:
        raise ValueError("Invalid DOT format")
    
    graph = graphs[0]
    
    # Extract existing nodes and sort them to create a mapping
    old_nodes = sorted(graph.get_nodes(), key=lambda n: int(n.get_name()))
    node_mapping = {node.get_name(): str(i + 1) for i, node in enumerate(old_nodes)}
    
    # Create a new graph with renamed nodes
    new_graph = pydot.Dot(graph_type="digraph")
    
    # Preserve node attributes
    for old_name, new_name in node_mapping.items():
        old_node = graph.get_node(old_name)[0]
        new_node = pydot.Node(new_name, **old_node.get_attributes())
        new_graph.add_node(new_node)
    
    # Preserve edges and their attributes (including angle)
    for edge in graph.get_edges():
        src, dst = edge.get_source(), edge.get_destination()
        attributes = edge.get_attributes()
        new_edge = pydot.Edge(node_mapping[src], node_mapping[dst])
        
        # Explicitly preserve all attributes, including angle
        for key, value in attributes.items():
            new_edge.set(key, value)
        
        new_graph.add_edge(new_edge)
    
    # Preserve subgraphs (rank constraints)
    for subgraph in graph.get_subgraphs():
        new_subgraph = pydot.Subgraph()
        if "rank" in subgraph.get_attributes():
            new_subgraph.set("rank", subgraph.get_attributes()["rank"])
        for node in subgraph.get_nodes():
            if node.get_name() in node_mapping:
                new_subgraph.add_node(pydot.Node(node_mapping[node.get_name()]))
        new_graph.add_subgraph(new_subgraph)
    
    return new_graph.to_string()

def process_dot_file(input_file, output_file):
    dot_content = read_dot_file(input_file)
    new_dot_content = rename_nodes(dot_content)
    write_dot_file(output_file, new_dot_content)
    print(f"Processed DOT file saved as: {output_file}")

# Example usage:
# process_dot_file('input.dot', 'output.dot')

process_dot_file('dat/diNet.dot', 'dat/output.dot')
