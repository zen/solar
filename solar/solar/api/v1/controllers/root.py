from pecan import expose, redirect
from pecan.rest import RestController


class BaseRestController(RestController):
    @expose(template='json')
    def options(self):
        return {
            'handlers': list(self._inspect_handlers()),
        }

    def _inspect_handlers(self, base_path=[]):
        for k, v in self.__class__.__dict__.items():
            if isinstance(v, BaseRestController):
                for h in v._inspect_handlers(base_path=base_path + [k]):
                    yield h

        yield {
            'methods': [
                method
                for method in ['get', 'post', 'put', 'delete', 'options']
                if hasattr(self.__class__, method)
            ],
            'path': '/{}'.format('/'.join(base_path)),
        }


class ConnectionsGraphController(BaseRestController):
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
                    'label': e[2],
                } for e in edges
            ]
        }


class ConnectionsController(BaseRestController):
    graph = ConnectionsGraphController()


class RootController(BaseRestController):
    connections = ConnectionsController()
