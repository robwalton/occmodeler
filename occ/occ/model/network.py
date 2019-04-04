import networkx as nx


def check_medium_graph(medium_graph):
    """Assert that g is an nx.Graph having contiguously numbered nodes starting from 0."""

    g = medium_graph
    assert isinstance(g, nx.Graph)
    for node in g.nodes:
        if not isinstance(node, int):
            raise AssertionError(f"node {node} must be of type 'int' not '{type(node)}."
                                 "Use destringizer=int with nx.read_gml()?'")
    assert list(g.nodes)[0] == 0, f"medium_graph nodes must be numbered from 0 not {list(g.nodes)[0]}"
    assert list(g.nodes) == list(range(len(g.nodes)))