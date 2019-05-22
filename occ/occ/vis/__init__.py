import plotly.offline as py

from occ.sim import SimulationResult
import occ.reduction
import occ.vis.occasion_graph


def iplot_causal_graph(sim_result: SimulationResult):

    place_change_events = occ.reduction.generate_place_increased_events(sim_result.places)
    transition_events = occ.reduction.generate_transition_events(sim_result.transitions)
    occasion_graph_ = occ.reduction.generate_causal_graph(
        place_change_events, transition_events, time_per_step=sim_result.sim_args.step)
    g = occ.vis.occasion_graph.generate_causal_graph_figure(occasion_graph_, sim_result.model.network)

    py.iplot(g)
