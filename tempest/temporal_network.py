import networkx as nx
from collections import defaultdict

EMPTY_EDGE = {'weight': 0}

class TemporalNetwork(nx.DiGraph):
    def __init__(self, incoming_graph_data=None, **attr):
        super().__init__(incoming_graph_data, **attr)

        self.snapshots = defaultdict(set)
        self.present = defaultdict(set)
        # self.locations = set()

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        _super_ret = super().add_edge(u_of_edge, v_of_edge, **attr)

        for loc, t in (u_of_edge, v_of_edge):
            self.snapshots[t].add(loc)
            self.present[loc].add(t)

        return _super_ret

    def nodes_at_time(self, t):
        return [(loc, t) for loc in self.snapshots[t]]
    
    def when_present(self, loc):
        return [(loc, t) for t in self.present[loc]]
    
    @classmethod
    def from_timenode_projection(cls, G:nx.DiGraph):
        TN = cls(G)
        for (u_loc, u_t), (v_loc, v_t) in G.edges:
            TN.snapshots[u_t].add(u_loc)
            TN.snapshots[v_t].add(v_loc)
            TN.present[u_loc].add(u_t)
            TN.present[v_loc].add(v_t)
        return TN

    @classmethod
    def read_graphml(cls, path, *args, **kwargs):
        def parse_tuple(tuple_str):
            loc, t = tuple_str.lstrip('(').rstrip(')').split(',')
            loc = loc.strip("'")
            return loc, int(t)

        G = nx.read_graphml(path, node_type=parse_tuple, *args, **kwargs)
        
        return cls.from_timenode_projection(G)

    def to_static(self):
        S = nx.DiGraph()
        Nt = len(self.snapshots)
        for loc, ts in self.present.items():
            S.add_node(loc, present=len(ts)/Nt)
            for t in ts:
                for (nbr_loc, nbr_t), weight in self[loc, t].items():
                    if loc != nbr_loc:
                        existing_weight = S.get_edge_data(loc, nbr_loc, EMPTY_EDGE)['weight']
                        new_weight = existing_weight + weight['weight']
                        S.add_edge(loc, nbr_loc, weight=new_weight)
        return S
