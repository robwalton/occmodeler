# occ: occasion modelling


## PLAN

### New Sacred less workflow:

1. Create model from
    1. Unit
    2. Network (multiplex later)
    3. Initial marking
2. Model to `.candl` text **NO: DONT NEED TO SEE THIS HERE**
2. Pass `.candl` along with simulation config to create a Simulation
3. Simulator Simulation runs in a tmp dir and returns a NamedTuple of
    1. place frame (or list of frames (or just the one frame with a repeat value))
    2. transitions frame of same
    
   option on simulator to not load places and transitions into frames. NO: replace with a results object which does load file unless actually used

   args specified as:
```python
from dataclasses import dataclass

@dataclass
class Model:
    unit: object
    network: nx.Graph  # multiple later. depends on unit
    marking: object

@dataclass
class Interval:
    start: float
    step: float
    stop: float


@dataclass
class SimArgs:
    interval: Interval
    runs: int
    
 
@dataclass
class Simulation:
    model: Model
    sim_args: SimArgs

@dataclass
class Results:
    places: pandas.df
    transitions: pandas.df

@dataclass
class SimulationRun:
    simulation: Simulation
    result: Results

```

We have no references to paths here. All objects

### And Sacred workflow:

Use SacredWrapper around Simulator to create Run dir, but otherwise looks the same.

```python
Archive()
```
These are Experiment records.

### Post experiment:

Both Sacred and non Sacred end up looking to the analysis code the same:
1. Model
    1. Unit (can't be read from archive yet)
    2. Initial marking (can't be read from archive yet)
    3. Network (later multiplex); optionally with position locations
2. Simulation configuration args
3. Results object which will load these if called
    1. places
    2. transitions
    3. a description of the column naming

We want no mention of the filesystem or MongoDB or whatever this is on here
### Transitions in models and reading the files

Table of Transition types supported with
1. Python class name
2. Naming scheme in transitions.csv
3. Occasion class when building the causal graph

Note we need to keep 2 and 3 synchronised.

### Packages

* petri (or snoopy, pyspike, or candl, or scpn)
    * model (needs to be more generic: i.e.)
    * sim
        * args (more than are exposed above)
        * spike call code
        * results - basic loading
    * sacred

* occ
    * model
        * transitions: FollowOne, FollowTwo...
        * marking ...
    * sim
        * args
        * Simulation
        * results (reduce or process or data)
            * places & transitions (tidy frame)
            * functions to pull out marking at any time
            * place changes
    * sacred
        * run simulation and archive
        * return results
        * load simulation, including results from archive (SimulationRun)

    * process
        * causal graph (transition types mirror those of occ.model)

    * vis
        * network view
        * counts
        * phase portrait
        * occasion graph
    * doc
        * this description of packages
        * API
        * ipython tutorial
        * sacred description

* occdash (dashboard for exploring results)

* occlab
    * model
        * launcher
        * microwave cavity
        * other tricks



```python

```

## Simulation

[Spike][spike] is used simulate Petri net models. To run a simulation requires an `.spc` file which specifies a list of commands for Spike. The model to simulate is given in a `.candl` file. When building models with repeated primitives and networks of neighbours.


To build a model:
```python

from pyspike.model import FollowNeighbour as follow1
from pyspike.model import FollowTwoNeighbours as follow2
from pyspike.model import UnitModel, u, n1, n2, Unit
from pyspike.model import marking


indexes = list(range(n_nodes()))
init1 = 3
init2 = 4

indexes.remove(init1)
indexes.remove(init2)

a = Unit.place('a', marking(indexes))
b = Unit.place('b', marking([init1, init2]))
m = UnitModel(name="one_plus_two_neighbour_diffusion", colors=[Unit], variables=[u, n1, n2],
              places=[a, b])
m.add_transitions_from([
    follow2(a, b, 1),
    follow1(a, b, .5),
])

return m
    

```

Add markings (these can also be added while creating `a` and `b`)

```python
indexes = list(range(n_nodes()))
init1 = 3
init2 = 4

indexes.remove(init1)
indexes.remove(init2)

```

return run_on_network(m, save_run=save_run)

def run_on_network(
        model, medium_graph=None, graph_name='two community',
        start=0, stop=10, step=.01, runs=1, repeat_sim=1,
        save_run=False):
    if not medium_graph:
        medium_graph = network()
    return call.run_experiment(
        model, medium_graph=medium_graph, graph_name=graph_name,
        start=start, stop=stop, step=step, runs=runs, repeat_sim=repeat_sim,
        calling_file=Path(__file__), file_storage_observer=save_run)



```



[spike]: https://www-dssz.informatik.tu-cottbus.de/DSSZ/Software/Spike


## Example files

These files are taken from run 180

### .spc
Spike's conf.spc specify a list of commands for Spike. For example:

`conf.spc`:
```
import: {
    from: "/var/folders/rb/z1vh8mr52xvc_y0yx4bw20jh0000gn/T/tmpdsibacc6/one_plus_two_neighbour_diffusion-on-two-community.candl"
}
configuration: {
    simulation: {
        name: "blank"
        type: stochastic
        solver: direct
        threads: 0
        interval: 0:0.01:10
        runs: 1
        export: {
            places: []
            to: "_spike/output/places.csv"
        }
        export: {
            transitions: []
            to: "_spike/output/transitions.csv"
        }
    }
}

```

### .candl

Spike's `.candl` file describes the model to simulate. It will be reverenced in a `conf.spc` file.

```
colspn  [one_plus_two_neighbour_diffusion on two community]
{
colorsets:
  Unit = {0..13};

variables:
  Unit : u;
  Unit : n1;
  Unit : n2;

colorfunctions:
bool  are_both_neighbours(Unit u,Unit n1,Unit n2) { (n1!=n2) & ((u=0 & (n1=1|n1=2|n1=5|n1=6) & (n2=1|n2=2|n2=5|n2=6)) | (u=1 & (n1=0|n1=2|n1=3|n1=6) & (n2=0|n2=2|n2=3|n2=6)) | (u=2 & (n1=0|n1=1|n1=3|n1=4|n1=6) & (n2=0|n2=1|n2=3|n2=4|n2=6)) | (u=3 & (n1=1|n1=2|n1=4|n1=5) & (n2=1|n2=2|n2=4|n2=5)) | (u=4 & (n1=2|n1=3|n1=5|n1=6) & (n2=2|n2=3|n2=5|n2=6)) | (u=5 & (n1=0|n1=3|n1=4|n1=6) & (n2=0|n2=3|n2=4|n2=6)) | (u=6 & (n1=0|n1=1|n1=2|n1=4|n1=5|n1=7) & (n2=0|n2=1|n2=2|n2=4|n2=5|n2=7)) | (u=7 & (n1=6|n1=8|n1=9|n1=11|n1=12|n1=13) & (n2=6|n2=8|n2=9|n2=11|n2=12|n2=13)) | (u=8 & (n1=7|n1=9|n1=10|n1=12|n1=13) & (n2=7|n2=9|n2=10|n2=12|n2=13)) | (u=9 & (n1=7|n1=8|n1=10|n1=11) & (n2=7|n2=8|n2=10|n2=11)) | (u=10 & (n1=8|n1=9|n1=11|n1=12) & (n2=8|n2=9|n2=11|n2=12)) | (u=11 & (n1=7|n1=9|n1=10|n1=12|n1=13) & (n2=7|n2=9|n2=10|n2=12|n2=13)) | (u=12 & (n1=7|n1=8|n1=10|n1=11|n1=13) & (n2=7|n2=8|n2=10|n2=11|n2=13)) | (u=13 & (n1=7|n1=8|n1=11|n1=12) & (n2=7|n2=8|n2=11|n2=12))) };
bool  is_neighbour(Unit u,Unit n1) { (u=0 & (n1=1|n1=2|n1=5|n1=6)) | (u=1 & (n1=0|n1=2|n1=3|n1=6)) | (u=2 & (n1=0|n1=1|n1=3|n1=4|n1=6)) | (u=3 & (n1=1|n1=2|n1=4|n1=5)) | (u=4 & (n1=2|n1=3|n1=5|n1=6)) | (u=5 & (n1=0|n1=3|n1=4|n1=6)) | (u=6 & (n1=0|n1=1|n1=2|n1=4|n1=5|n1=7)) | (u=7 & (n1=6|n1=8|n1=9|n1=11|n1=12|n1=13)) | (u=8 & (n1=7|n1=9|n1=10|n1=12|n1=13)) | (u=9 & (n1=7|n1=8|n1=10|n1=11)) | (u=10 & (n1=8|n1=9|n1=11|n1=12)) | (u=11 & (n1=7|n1=9|n1=10|n1=12|n1=13)) | (u=12 & (n1=7|n1=8|n1=10|n1=11|n1=13)) | (u=13 & (n1=7|n1=8|n1=11|n1=12)) };

places:
discrete:
  Unit a = 0++1++2++5++6++7++8++9++10++11++12++13;
  Unit b = 3++4;

transitions:
  f2ab
 {[are_both_neighbours(u, n1, n2)]}
    : [b >= {n1++n2}]
    : [b + {u}] & [a - {u}]
    : 1
    ;
  f1ab
 {[is_neighbour(u, n1)]}
    : [b >= {n1}]
    : [b + {u}] & [a - {u}]
    : 0.5
    ;

}
```