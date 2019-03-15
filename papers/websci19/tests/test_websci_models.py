import os
from pathlib import Path

import pyspike
from pyspike import tidydata
from occ.model import FollowNeighbour as follow1, FollowTwoNeighbours as follow2, ModulatedInternal as modulated_internal
from pyspike.model import UnitModel, u, n1, n2, Unit
from pyspike.model import marking
import plotly.offline as py
import plotly.graph_objs as go

import pyspike
from pyspike import tidydata
import pyspike.util

from pyspike.util import render_name


import websci19
import websci19.models



N_NODES = websci19.MEDIUM_GRAPH.number_of_nodes()


run_on_tos_network = websci19.create_run_on_tos_network_function(Path(__file__))



def test_generate_pair_with_random_markings__visual_only():
    a, A = websci19.models.generate_pair_with_random_markings('a', 'A', 10)
    print('****')
    print('a', a.initial_marking)
    print('A', A.initial_marking)
    print('****')


def test_generate_generate_pair_with_marking():
    a, A = websci19.models.generate_pair_with_marking('a', 'A', 10, [1, 3, 5, 7, 9])
    assert a.initial_marking == "1++3++5++7++9"
    assert A.initial_marking == "0++2++4++6++8"




# 0. Conformation that TOS graph has a stable state for 100% 2 neighbour following and definition of pole 1 and pole 2


class TestDiffusionAndMultilayeredDiffusionFromOneEnd:

    def test_diffusion_from_one_end_on_to_graph(self):
        indexes = list(range(N_NODES))
        indexes.remove(1)
        a = Unit.place('a', marking(indexes))
        b = Unit.place('b', marking([1]))
        m = UnitModel(name="diffusion_from_one_end", colors=[Unit], variables=[u, n1, n2],
                      places=[a, b])
        m.add_transitions_from([
            follow1(a, b, use_read_arc=False)
        ])
        run_on_tos_network(m)

    def test_multiphase_diffusion_from_one_end_on_to_graph(self):
        indexes = list(range(N_NODES))
        for i in [26, 27, 28, 29]:
            indexes.remove(i)

        a = Unit.place('a', marking(indexes))
        b = Unit.place('b', marking([26, 27, 29]))
        c = Unit.place('c', marking([28]))
        m = UnitModel(name="diffusion_from_one_end", colors=[Unit], variables=[u, n1, n2],
                      places=[a, b])
        m.add_transitions_from([
            follow1(a, b),
            follow1(b, c)
        ])
        run_on_tos_network(m)

    def test_multiphase_diffusion_from_one_end_on_to_graph_with_read_arc__will_confuse_readers_but_just_to_test(self):
        indexes = list(range(N_NODES))
        indexes.remove(28)

        a = Unit.place('a', marking(indexes))
        b = Unit.place('b', marking([28]))
        c = Unit.place('c', marking([28]))
        m = UnitModel(name="diffusion_from_one_end", colors=[Unit], variables=[u, n1, n2],
                      places=[a, b])
        m.add_transitions_from([
            follow1(a, b, use_read_arc=True),
            follow1(b, c, use_read_arc=True)
        ])
        run_on_tos_network(m)


POLE1_NODES = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
POLE2_NODES = list(range(30))
for i in POLE1_NODES:
    POLE2_NODES.remove(i)


class TestConvergenceFromNoiseAndEchoChamberLikeBehaviour:

    def test_1_neighbour_only(self):
        a, A = websci19.models.generate_pair_with_random_markings('a', 'A', N_NODES)
        m = UnitModel(name="convergence from noise follow 1 neighbour only", colors=[Unit], variables=[u, n1, n2], places=[a, A])
        m.add_transitions_from([
            follow1(a, A),
            follow1(A, a),
        ])
        run_on_tos_network(m)

    def test_2_neighbour_only(self):
        a, A = websci19.models.generate_pair_with_random_markings('a', 'A', N_NODES)
        m = UnitModel(name="convergence from noise follow 2 neighbour only", colors=[Unit], variables=[u, n1, n2], places=[a, A])
        m.add_transitions_from([
            follow2(a, A, 2),
            follow2(A, a, 2),
        ])
        run_on_tos_network(m)

    def test_2_neighbour_only_for_stable_initial_markings(self):

        a, A = websci19.models.generate_pair_with_marking('a', 'A', N_NODES, [26, 27, 28, 29])
        m = UnitModel(name="convergence from noise follow 2 neighbour only", colors=[Unit], variables=[u, n1, n2], places=[a, A])
        m.add_transitions_from([
            # follow2(a, A),
            follow2(A, a),
        ])
        run_on_tos_network(m)
        """GREAT!
        Starting with A on 26, 27, 28, 29...
        We see A diffusing across a, but it becomes stuck and cannot reach the nodes
        11 - 21
        """




    def test_2_neighbour_only_for_stable_initial_markings_step_2(self):
        """
        Having just identified POLE1_NODES and POLE2_NODES by starting a run from one end (now called Pole2)
        lets check that pole 1 won't spread
        :return:
        """

        a, A = websci19.models.generate_pair_with_marking('a', 'A', N_NODES, POLE1_NODES)
        m = UnitModel(name="convergence from noise follow 2 neighbour only", colors=[Unit], variables=[u, n1, n2], places=[a, A])
        m.add_transitions_from([
            # follow2(a, A),
            follow2(A, a),
        ])
        run_on_tos_network(m)
        """
        """

    def test_2_neighbour_only_small_graph(self):
        raise AssertionError("Inlude the small contrived networks used for early testing here. These include those in e.g. test_temporal.py")

    def test_1_and_2_neighbours(self):
        a, A = websci19.models.generate_pair_with_random_markings('a', 'A', N_NODES)
        m = UnitModel(name="convergence from noise follow 2 neighbour only", colors=[Unit], variables=[u, n1, n2], places=[a, A])
        m.add_transitions_from([
            follow1(a, A),
            follow1(A, a),
            follow2(a, A, 2),
            follow2(A, a, 2),
        ])
        run_on_tos_network(m)

    # NOTE: run and saved as run 160
    def skip_test_1_and_2_neighbours_with_100_runs(self):
        a, A = websci19.models.generate_pair_with_random_markings('a', 'A', N_NODES)
        m = UnitModel(name="convergence from noise follow 2 neighbour only", colors=[Unit], variables=[u, n1, n2], places=[a, A])
        m.add_transitions_from([
            follow1(a, A),
            follow1(A, a),
            follow2(a, A, 2),
            follow2(A, a, 2),
        ])
        run_on_tos_network(m, repeat_sim=100, save_run=True)

    # NOTE: run and saved as run 161
    def skip_test_1_and_2_neighbour_for_stable_initial_markings_100_runs(self):


        a, A = websci19.models.generate_pair_with_marking('a', 'A', N_NODES, POLE1_NODES)
        m = UnitModel(name="blah", colors=[Unit], variables=[u, n1, n2], places=[a, A])
        m.add_transitions_from([
            follow1(a, A, 0.2),
            follow1(A, a, 0.2),
            follow2(a, A, 2),
            follow2(A, a, 2),
        ])
        run_on_tos_network(m, repeat_sim=100, save_run=True)
        """
        """


    # Run and saved as run 162: check the analysis with this
    def test_wtf_162(self):

        a, A = websci19.models.generate_pair_with_marking('a', 'A', N_NODES, POLE1_NODES)
        m = UnitModel(name="blah", colors=[Unit], variables=[u, n1, n2], places=[a, A])
        m.add_transitions_from([
            # follow1(a, A, 0.2),
            # follow1(A, a, 0.2),
            follow2(a, A, 2),
            follow2(A, a, 2),
        ])
        run_on_tos_network(m, repeat_sim=10, save_run=True)
        """
        """



class TestConflationOfIssuesOn12NeighbourFollowing:

    def test_two_issues_non_conflated(self):
        a, A = websci19.models.generate_pair_with_random_markings('a', 'A', N_NODES, pos_offset=(0, -.05))
        b, B = websci19.models.generate_pair_with_random_markings('b', 'B', N_NODES, pos_offset=(0, +.05))
        m = UnitModel(name="convergence from noise two issues non conflated", colors=[Unit], variables=[u, n1, n2],
                      places=[a, A, b, B])

        m.add_transitions_from([
            follow1(a, A),
            follow1(A, a),
            follow2(a, A, 2),
            follow2(A, a, 2),
            follow1(b, B),
            follow1(B, b),
            follow2(b, B, 2),
            follow2(B, b, 2),
        ])
        run_on_tos_network(m)

    def triangle_coords_around_zero(self, edge_width):
        a = (-.5 * edge_width, -edge_width * .866 / 2)
        b = (.5 * edge_width, -edge_width * .866 / 2)
        c = (0 * edge_width, edge_width * 0.866 / 2)
        return a, b, c


    def test_two_issues_conflated_by_emotion(self):

        a_off, b_off, e_off = self.triangle_coords_around_zero(.05)
        # a, A = websci19.models.generate_pair_with_random_markings('a', 'A', N_NODES, pos_offset=a_off)
        # b, B = websci19.models.generate_pair_with_random_markings('b', 'B', N_NODES, pos_offset=b_off)
        #
        e, E = websci19.models.generate_pair_with_marking('e', 'E', N_NODES, POLE1_NODES, pos_offset=e_off)
        a, A = websci19.models.generate_pair_with_marking('a', 'A', N_NODES, POLE1_NODES, pos_offset=e_off)
        b, B = websci19.models.generate_pair_with_marking('b', 'B', N_NODES, POLE1_NODES, pos_offset=e_off)

        m = UnitModel(name="convergence from noise two issues conflated", colors=[Unit], variables=[u, n1, n2],
                      places=[a, A, b, B, e, E])

        r_f1 = 0.5
        r_f2 = 1
        r_e_f1 = r_f1
        r_e_f2 = r_f2
        r_ab_to_e = 1

        m.add_transitions_from([
            follow1(a, A, r_f1, enabled_by_local=E),
            follow1(A, a, r_f1, enabled_by_local=e),
            follow2(a, A, r_f2, enabled_by_local=E),
            follow2(A, a, r_f2, enabled_by_local=e),
            follow1(b, B, r_f1, enabled_by_local=E),
            follow1(B, b, r_f1, enabled_by_local=e),
            follow2(b, B, r_f2, enabled_by_local=E),
            follow2(B, b, r_f2, enabled_by_local=e),
            follow1(e, E, r_e_f1),
            follow1(E, e, r_e_f1),
            follow2(e, E, r_e_f2),
            follow2(E, e, r_e_f2),
            modulated_internal(A, a, e, r_ab_to_e),
            modulated_internal(B, b, e, r_ab_to_e),
            modulated_internal(a, A, E, r_ab_to_e),
            modulated_internal(b, B, E, r_ab_to_e),
        ])
        run_on_tos_network(m, start=0, stop=5, step=.02, runs=1000)
        assert False

    def test_two_coupled_directly_using_modulated_internal(self):
        pass

    def test_two_coupled_directly_using_ab_AB(self):
        a_off, b_off, x_off = self.triangle_coords_around_zero(.05)

        a, A = websci19.models.generate_pair_with_marking('a', 'A', N_NODES, POLE1_NODES, pos_offset=a_off)
        b, B = websci19.models.generate_pair_with_marking('b', 'B', N_NODES, POLE1_NODES, pos_offset=b_off)
        x, X = websci19.models.generate_pair_with_marking('x', 'X', N_NODES, POLE1_NODES, pos_offset=x_off)
        m = UnitModel(name="convergence from noise two issues conflated", colors=[Unit], variables=[u, n1, n2],
                      places=[a, A, b, B, x, X])

        m.add_transitions_from([
            # External influence
            follow1(a, A),
            follow1(A, a),
            follow2(a, A, 2),
            follow2(A, a, 2),
            follow1(b, B),
            follow1(B, b),
            follow2(b, B, 2),
            follow2(B, b, 2),


            # Drive the larger
            modulated_internal(x, X, A, activate2=B, rate=2),
            modulated_internal(X, x, a, activate2=b, rate=2),
            modulated_internal(A, a, x),
            modulated_internal(B, b, x),
            modulated_internal(a, A, X),
            modulated_internal(b, B, X),
        ])
        run_on_tos_network(m, runs=1000, start=0, stop=10, step=.1)

    def test_a_model_in_which_nodes_fight_back_while_loosing(self):
        """
        This could be either at the in individual level but ideally at the group level.
        Intuitively we need a derivative: whereby if our lowercaseness is waining then
        we defend our view by shouting or by pulling both ourselves and neiwgbours back
        to our old state.
        """

    def test_a_model_in_which_we_list_less_to_people_with_opposing_xX_views(self):
        """
        xX from model above. if a node has 1 or 2 neigbours with differing xX view
        then pay them less attention. Is it the same to pay them more attention if
        they share the same xy view? I feel not.
        :return:
        """


class InterestingPrediction:

    # We predict with an unproved method and
    def test_result(self):
        assert False
        # Start just eE alone from its fully separated initial condition

    def test_some_marking_of_any_pair_to_show_that_it_is_stable_forever(self):
        pass
        """With follow2 only. There may be more than one of these, but we seek to
        find only 1 for now. Later we might try finding them all, perhaps by setting 
        a very low r_f1/r_f2.
        """

    def test_do_a_monte_carlo_to_see_how_long_it_lasts_by_itself(self):
        """
        Later we might want to run may runs and create a statstical distribution
        of its lifespan
        :return:
        """

    def test_next_add_a_conflated_argument_in_and_see_if_it_lasts_longer(self):

        """
        Note: In our model there is some asymettry here. We should look for a model
        in which just two
        :return:
        """

class TestFutureExperiments:
    """

    """
    pass

# %% Conflation of issue
#   - Two issues conflated by emotion
#   - the eye diagram with axes being the difference between counts for a+ and b+ for each pole.
#   - OR just plot the sum of number of places which differ for each a and b.



