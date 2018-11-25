import json
from textwrap import dedent
from collections import OrderedDict

from pyspike.spcconf import od_to_spc
import pyspike.spcconf


OD = OrderedDict


def args_to_od_call(include_model=False):

    model_path = 'model/diffusion_2D4.andl'

    sim_args = {
        "name": "Diffusion",
        "type": "stochastic",
        "solver": "direct",
        "threads": 0,
        "interval": {
            "start": 0,
            "step": 0.1,
            "stop": 10
        },
        "runs": 100,
        "export": [
            {
                "places": [],
                "to": "places.csv"
            },
            {
                "transitions": [],
                "to": "transitions.csv"
            }
        ]
    }
    if include_model:
        model_args = {
            'constants': {
                'all': {
                    'D': 3,
                    'M': 'D/2'
                }
            },
            'places': {
                'P': '1000`(M,M)'
            }
        }
    else:
        model_args = {}

    return pyspike.spcconf.args_to_od(model_path, model_args, sim_args)


class TestArgsToOD(object):

    def test_import(self):
        assert IMPORT == args_to_od_call()['import']
        assert IMPORT == args_to_od_call(include_model=True)['import']

    def test_top_level_order(self):
        keys = list(args_to_od_call().keys())
        assert ['import', 'configuration'] == keys
        keys = list(args_to_od_call(include_model=True).keys())
        assert ['import', 'configuration'] == keys

    def test_configuration_order(self):
        keys = list(args_to_od_call()['configuration'].keys())
        assert ['simulation'] == keys

    def test_configuration_order_with_model(self):
        keys = list(args_to_od_call(include_model=True)['configuration'].keys())
        assert ['model', 'simulation'] == keys

    def test_simulation_order(self):
        sim = args_to_od_call()['configuration']['simulation']
        assert ['name', 'type', 'solver', 'threads', 'interval', 'runs', 'export'] == list(sim.keys())

    def test_model(self):
        model = args_to_od_call(include_model=True)['configuration']['model']
        assert model == {'constants': {'all': {'D': 3, 'M': 'D/2'}}, 'places': {'P': '1000`(M,M)'}}

    def test_simulation_up_exports(self):
        sim = args_to_od_call()['configuration']['simulation']
        del sim['export']
        expected = OD([
            ('name', 'Diffusion'),
            ('type', 'stochastic'),
            ('solver', 'direct'),
            ('threads', 0),
            ('interval', OD(start=0, step=0.1, stop=10)),
            ('runs', 100),
        ])
        assert expected == sim

    def test_export_list(self):
        export_list = args_to_od_call()['configuration']['simulation']['export']
        assert 2 == len(export_list)
        assert {'places': [], 'to': 'places.csv'} == export_list[0]
        assert {'transitions': [], 'to': 'transitions.csv'} == export_list[1]


###########


IMPORT = OD([('from', 'model/diffusion_2D4.andl')])
MODEL = OD([('constants', OD(all=OD([('D', 3), ('M', 'D/2')]))), ('places', {'P': '1000`(M,M)'})])
EXPORT1 = OD(places=[], to='spike/output/places.csv')
EXPORT2 = OD(places=["Grid2D"], to='spike/output/coloured-places.csv')
EXPORT3 = OD(transitions=[], to='spike/output/transitions.csv')
INTERVAL = OD(start=0, step=0.1, stop=10)
SIMULATION = OD([
    ('name', 'Diffusion'),
    ('type', 'stochastic'),
    ('solver', 'direct'),
    ('threads', 0),
    ('interval', INTERVAL),
    ('runs', 100),
    ('export', [EXPORT1, EXPORT2, EXPORT3])
])
CONFIGURATION = OD(OD([('model', MODEL),('simulation', SIMULATION)]))
INTEGRATION = OD([('import', IMPORT), ('configuration', CONFIGURATION)])

INTEGRATION_SPC = '''\
import: {
    from: "model/diffusion_2D4.andl"
}
configuration: {
    model: {
        constants: {
            all: {
                D: "3"
                M: "D/2"
            }
        }
        places: {
            P: "1000`(M,M)"
        }
    }
    simulation: {
        name: "Diffusion"
        type: stochastic
        solver: direct
        threads: 0
        interval: 0:0.1:10
        runs: 100
        export: {
            places: []
            to: "spike/output/places.csv"
        }
        export: {
            places: ["Grid2D"]
            to: "spike/output/coloured-places.csv"
        }
        export: {
            transitions: []
            to: "spike/output/transitions.csv"
        }
    }
}'''


class TestODToSpc(object):

    def test_to_spc_import_only(self):
        od = OD([('import', IMPORT)])

        assert od_to_spc(od) == dedent('''\
        import: {
            from: "model/diffusion_2D4.andl"
        }''')

    def test_to_spc_simulation_with_no_exports_or_interval(self):
        simulation = OD([('name', 'Diffusion'),
                         ('type', 'stochastic'),
                         ('solver', 'direct'),
                         ('threads', 0),
                         ('runs', 100)])

        od = OD(configuration=OD(simulation=simulation))
        assert od_to_spc(od) == dedent('''\
        configuration: {
            simulation: {
                name: "Diffusion"
                type: stochastic
                solver: direct
                threads: 0
                runs: 100
            }
        }''')

    def test_to_spc_simulation_with_interval(self):
        simulation = OD([('type', 'stochastic'),
                         ('interval', INTERVAL)])

        od = OD(configuration=OD(simulation=simulation))
        assert od_to_spc(od) == dedent('''\
        configuration: {
            simulation: {
                type: stochastic
                interval: 0:0.1:10
            }
        }''')

    def test_to_spc_simulation_with_exports(self):
        simulation = OD([('type', 'stochastic'),
                         ('export', [EXPORT1, EXPORT2, EXPORT3])])

        od = OD(configuration=OD(simulation=simulation))
        assert od_to_spc(od) == dedent('''\
        configuration: {
            simulation: {
                type: stochastic
                export: {
                    places: []
                    to: "spike/output/places.csv"
                }
                export: {
                    places: ["Grid2D"]
                    to: "spike/output/coloured-places.csv"
                }
                export: {
                    transitions: []
                    to: "spike/output/transitions.csv"
                }
            }
        }''')

    def test_to_spc_integration(self):
        print('---')
        print(od_to_spc(INTEGRATION))
        print('---')
        assert od_to_spc(INTEGRATION) == INTEGRATION_SPC
