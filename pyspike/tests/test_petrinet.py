
import networkx as nx
from pytest import raises

from pyspike.petrinet import graph_to_func, graph_to_arc_expression, generate_candl_file_from_template


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

# colorfunctions:
# bool  is_neighbour(Unit u,Unit n) { (u=0 & (n=1|n=2|n=28|n=29)) | (u=1 & (n=0|n=2|n=3|n=29)) | (u=2 & (n=0|n=1|n=3|n=4|n=20|n=25)) | (u=3 & (n=1|n=2|n=4|n=6)) | (u=4 & (n=2|n=3|n=5|n=6)) | (u=5 & (n=4|n=6|n=7|n=10)) | (u=6 & (n=3|n=4|n=5|n=7|n=8|n=23)) | (u=7 & (n=5|n=6|n=8|n=9)) | (u=8 & (n=6|n=7|n=10|n=17)) | (u=9 & (n=7|n=10|n=11)) | (u=10 & (n=5|n=8|n=9|n=12)) | (u=11 & (n=9|n=12|n=13|n=21)) | (u=12 & (n=10|n=11|n=13|n=14)) | (u=13 & (n=11|n=12|n=14|n=15|n=18)) | (u=14 & (n=12|n=13|n=15|n=16)) | (u=15 & (n=13|n=14|n=16|n=17)) | (u=16 & (n=14|n=15|n=17|n=18)) | (u=17 & (n=8|n=15|n=16|n=18|n=19)) | (u=18 & (n=13|n=16|n=17|n=19|n=20)) | (u=19 & (n=17|n=18|n=21)) | (u=20 & (n=2|n=18|n=21)) | (u=21 & (n=11|n=19|n=20|n=22)) | (u=22 & (n=21|n=23|n=24)) | (u=23 & (n=6|n=22|n=25)) | (u=24 & (n=22|n=25|n=26)) | (u=25 & (n=2|n=23|n=24|n=27)) | (u=26 & (n=24|n=27|n=28)) | (u=27 & (n=25|n=26|n=28|n=29)) | (u=28 & (n=0|n=26|n=27|n=29)) | (u=29 & (n=0|n=1|n=27|n=28)) };


CANDL_TEMPLATE = '''abc
colorfunctions:
bool  is_neighbour(Unit u,Unit n) {$FUNC$}
def
'''

CANDL_DESIRED = '''abc
colorfunctions:
bool  is_neighbour(Unit u,Unit n) { (u=1 & (n=2|n=3)) | (u=2 & (n=1|n=3)) | (u=3 & (n=1|n=2|n=4)) | (u=4 & (n=3)) }
def
'''


class TestGenerateCandlFileFromTemplate(object):

    def test_with_network(self):
        g = nx.Graph()
        g.add_edge(1, 2)
        g.add_edge(2, 3)
        g.add_edge(3, 1)
        g.add_edge(3, 4)
        result = generate_candl_file_from_template(CANDL_TEMPLATE, g)
        assert result == CANDL_DESIRED

    def test_with_invalid_template(self):
        with raises(Exception):
            generate_candl_file_from_template('no dollar funcs in here!', nx.Graph())
