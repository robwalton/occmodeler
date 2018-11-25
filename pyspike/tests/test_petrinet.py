
import networkx as nx
from pyspike.petrinet import graph_to_func, graph_to_arc_expression



def log(s):
    print('---')
    print(s)
    print('---')

class TestGraphToFunc(object):

    def test_empty(self):
        g = nx.Graph()
        g.add_nodes_from([1, 2, 3])
        assert graph_to_func(g) == ''

    def test_pair(self):
        g = nx.Graph()
        g.add_edge(4, 5)
        assert graph_to_func(g) == '(x=4 & (y=5)) | (x=5 & (y=4))'

    def test_four(self):
        g = nx.Graph()
        g.add_edge(1, 2)
        g.add_edge(2, 3)
        g.add_edge(3, 1)
        g.add_edge(3, 4)
        assert graph_to_func(g) == '(x=1 & (y=2|y=3)) | (x=2 & (y=1|y=3)) | (x=3 & (y=1|y=2|y=4)) | (x=4 & (y=3))'

    def test_six_loop(self):
        g = nx.Graph()
        for i in range(1, 6):
            g.add_edge(i, i+1)
        g.add_edge(6, 1)

        assert graph_to_func(g) == (
                '(x=1 & (y=2|y=6)) | (x=2 & (y=1|y=3)) | '
                '(x=3 & (y=2|y=4)) | (x=4 & (y=3|y=5)) | '
                '(x=5 & (y=4|y=6)) | (x=6 & (y=1|y=5))')

        print(graph_to_func(g))


    def test_12_loop(self):
        g = nx.Graph()
        for i in range(1, 12):
            g.add_edge(i, i + 1)
        g.add_edge(12, 1)

        print()
        print(graph_to_func(g))
        print()


class TestGraphToArcExpression(object):

    def test_empty(self):
        g = nx.Graph()
        g.add_nodes_from([1, 2, 3])
        assert graph_to_arc_expression(g) == ''

    def test_pair(self):
        g = nx.Graph()
        g.add_edge(4, 5)
        assert graph_to_arc_expression(g) == '[u=4](5,m)++[u=5](4,m)'

    def test_four(self):
        g = nx.Graph()
        g.add_edge(1, 2)
        g.add_edge(2, 3)
        g.add_edge(3, 1)
        g.add_edge(3, 4)
        log(graph_to_arc_expression(g))
        assert graph_to_arc_expression(g) == '[u=1](2,m)++[u=1](3,m)++[u=2](1,m)++[u=2](3,m)++[u=3](1,m)++[u=3](2,m)++[u=3](4,m)++[u=4](3,m)'

    def test_six_loop(self):
        g = nx.Graph()
        for i in range(1, 6):
            g.add_edge(i, i+1)
        g.add_edge(6, 1)

        log(graph_to_arc_expression(g))
        assert graph_to_arc_expression(g) == '[u=1](2,m)++[u=1](6,m)++[u=2](1,m)++[u=2](3,m)++[u=3](2,m)++[u=3](4,m)++[u=4](3,m)++[u=4](5,m)++[u=5](4,m)++[u=5](6,m)++[u=6](1,m)++[u=6](5,m)'

    def test_12_loop(self):
        g = nx.Graph()
        for i in range(1, 12):
            g.add_edge(i, i + 1)
        g.add_edge(12, 1)

        log(graph_to_arc_expression(g))



# class TestGraphToArcExpression(object):

#     def test_empty(self):
#         g = nx.Graph()
#         g.add_nodes_from([1, 2, 3])
#         assert graph_to_arc_expression(g) == ''

#     def test_pair(self):
#         g = nx.Graph()
#         g.add_edge(4, 5)
#         assert graph_to_arc_expression(g) == '[u=4]((5,m)) ++ [u=5]((4,m))'

#     def test_four(self):
#         g = nx.Graph()
#         g.add_edge(1, 2)
#         g.add_edge(2, 3)
#         g.add_edge(3, 1)
#         g.add_edge(3, 4)
#         log(graph_to_arc_expression(g))
#         assert graph_to_arc_expression(g) == '[u=1]((2,m)++(3,m)) ++ [u=2]((1,m)++(3,m)) ++ [u=3]((1,m)++(2,m)++(4,m)) ++ [u=4]((3,m))'

#     def test_six_loop(self):
#         g = nx.Graph()
#         for i in range(1, 6):
#             g.add_edge(i, i+1)
#         g.add_edge(6, 1)

#         log(graph_to_arc_expression(g))
#         assert graph_to_arc_expression(g) == ('[u=1]((2,m)++(6,m)) ++ [u=2]((1,m)++(3,m)) ++ [u=3]((2,m)++(4,m)) ++ [u=4]((3,m)++(5,m)) ++ [u=5]((4,m)++(6,m)) ++ [u=6]((1,m)++(5,m))')

#     def test_12_loop(self):
#         g = nx.Graph()
#         for i in range(1, 12):
#             g.add_edge(i, i + 1)
#         g.add_edge(12, 1)

#         log(graph_to_arc_expression(g))