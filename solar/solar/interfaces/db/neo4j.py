import json
from copy import deepcopy
from enum import Enum
import py2neo

from solar.core import log


class Neo4jDB(object):
    COLLECTIONS = Enum(
        'Collections',
        'input resource state_data state_log'
    )
    DEFAULT_COLLECTION=COLLECTIONS.resource
    RELATION_TYPES = Enum(
        'RelationTypes',
        'input_to_input resource_input'
    )
    DEFAULT_RELATION=RELATION_TYPES.resource_input
    DB = {
        'host': 'localhost',
        'port': 7474,
    }
    NEO4J_CLIENT = py2neo.Graph

    def __init__(self):
        self._r = self.NEO4J_CLIENT('http://{host}:{port}/db/data/'.format(
            **self.DB
        ))
        self.entities = {}

    @staticmethod
    def _args_to_db(args):
        return {
            k: json.dumps(v) for k, v in args.items()
        }

    @staticmethod
    def _args_from_db(db_args):
        return {
            k: json.loads(v) for k, v in db_args.items()
        }

    @staticmethod
    def obj_to_db(o):
        o.properties = Neo4jDB._args_to_db(o.properties)

    @staticmethod
    def obj_from_db(o):
        o.properties = Neo4jDB._args_from_db(o.properties)

    def all(self, collection=DEFAULT_COLLECTION):
        return [
            r.n for r in self._r.cypher.execute(
                'MATCH (n:%(collection)s) RETURN n' % {
                    'collection': collection.name,
                }
            )
        ]

    def all_relations(self, type_=DEFAULT_RELATION):
        return [
            r.r for r in self._r.cypher.execute(
                *self._relations_query(
                    source=None, dest=None, type_=type_
                )
            )
        ]

    def clear(self):
        log.log.debug('Clearing whole DB')

        self._r.delete_all()

    def clear_collection(self, collection=DEFAULT_COLLECTION):
        log.log.debug('Clearing collection %s', collection.name)

        # TODO: make single DELETE query
        self._r.delete([r.n for r in self.all(collection=collection)])

    def create(self, name, args={}, collection=DEFAULT_COLLECTION):
        log.log.debug(
            'Creating %s, name %s with args %s',
            collection.name,
            name,
            args
        )

        properties = deepcopy(args)
        properties['name'] = name

        n = py2neo.Node(collection.name, **properties)
        self._r.create(n)

        return n

    def create_relation(self, source, dest, args={}, type_=DEFAULT_RELATION):
        log.log.debug(
            'Creating %s from %s to %s with args %s',
            type_.name,
            source.properties['name'],
            dest.properties['name'],
            args
        )
        r = py2neo.Relationship(source, type_.name, dest, **args)
        self._r.create(r)

        return r

    def _nodes_query(self,
                     name,
                     collection=DEFAULT_COLLECTION,
                     query_type='MATCH',
                     operation_type='RETURN'):
        kwargs = {
            'name': name,
        }

        query = ('%(query_type)s (n:%(collection)s {name:{name}}) '
                 '%(operation_type)s n' % {
                    'collection': collection.name,
                    'query_type': query_type,
                    'operation_type': operation_type,
                })

        return query, kwargs

    def get(self, name, collection=DEFAULT_COLLECTION):
        query, kwargs = self._nodes_query(
            name, collection=collection
        )
        res = self._r.cypher.execute(query, kwargs)

        if res:
            return res[0].n

    def get_or_create(self, name, args={}, collection=DEFAULT_COLLECTION):
        log.log.debug(
            'Get or create node %s, name %s with args %s',
            collection.name,
            name,
            args
        )

        query, kwargs = self._nodes_query(
            name, collection=collection, query_type='MERGE'
        )

        n = self._r.cypher.execute(query, kwargs)[0].n

        if args != n.properties:
            n.properties.update(args)
            n.push()
        return n

    def _relations_query(self,
                         source=None,
                         dest=None,
                         type_=DEFAULT_RELATION,
                         query_type='MATCH',
                         operation_type='RETURN'):
        kwargs = {}
        source_query = '()'
        if source:
            source_query = '(n {name:{source_name}})'
            kwargs['source_name'] = source.properties['name']
        dest_query = '()'
        if dest:
            dest_query = '(m {name:{dest_name}})'
            kwargs['dest_name'] = dest.properties['name']
        rel_query = '[r:%(type_)s]' % {'type_': type_.name}

        query = ('%(query_type)s %(source_query)s-%(rel_query)s->'
                 '%(dest_query)s %(operation_type)s r' % {
                     'dest_query': dest_query,
                     'operation_type': operation_type,
                     'query_type': query_type,
                     'rel_query': rel_query,
                     'source_query': source_query,
                     })

        return query, kwargs

    def delete_relations(self, source=None, dest=None, type_=DEFAULT_RELATION):
        query, kwargs = self._relations_query(
            source=source, dest=dest, type_=type_, operation_type='DELETE'
        )

        self._r.cypher.execute(query, kwargs)

    def get_relations(self, source=None, dest=None, type_=DEFAULT_RELATION):
        query, kwargs = self._relations_query(
            source=source, dest=dest, type_=type_
        )

        res = self._r.cypher.execute(query, kwargs)

        return [r.r for r in res]

    def get_or_create_relation(self,
                               source,
                               dest,
                               args={},
                               type_=DEFAULT_RELATION):
        log.log.debug(
            'Get or create relation %s from %s to %s with args %s',
            type_.name,
            source.properties['name'],
            dest.properties['name'],
            args
        )
        query, kwargs = self._relations_query(
            source=source, dest=dest, type_=type_, query_type='MERGE'
        )

        rel = self._r.cypher.execute(query, kwargs)

        r = rel[0].r
        if args != r.properties:
            r.properties.update(args)
            r.push()
        return r
