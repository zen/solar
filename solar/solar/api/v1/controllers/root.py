from pecan import expose, redirect
from pecan.rest import RestController


class ConnectionsGraphController(RestController):
    @expose(template='json')
    def get(self):
        """Dumps JSON to static directory for use in the UI viewer.
        """
        from solar.core import signals

        g = signals.detailed_connection_graph()

        edges = set([
            (e[0], e[1], v['label'])
            for e in g.edges()
            for v in g.get_edge_data(*e).values()
        ])

        return {
            'nodes': [{'id': node} for node in g.nodes()],
            'edges': [
                {
                    'source': e[0],
                    'target': e[1],
                    'label': e[2]
                } for e in edges
            ]
        }


class ConnectionsController(RestController):
    graph = ConnectionsGraphController()


class RootController(RestController):
    connections = ConnectionsController()
